import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from .Backend import TensorBackend
from .utils import quantize_tensor, quantize_bias


class RTLConv2dWrapper(nn.Module):
    """Wrap Conv2d with quantization and RTL backend execution"""

    def __init__(
        self,
        conv,
        backend=None,
        bitwidth=8,
        format="int",
        layer_name: str | None = None,
    ):
        super().__init__()
        self.stride = conv.stride
        self.padding = conv.padding
        self.kernel_size = conv.kernel_size
        self.weight = conv.weight
        self.bias = conv.bias
        self.bitwidth = bitwidth
        self.format = format
        self.layer_name = layer_name
        self.backend = TensorBackend(bitwidth, format)

    def forward(self, x):
        B, C, H, W = x.shape
        KH, KW = self.kernel_size
        out_h = (H + 2 * self.padding[0] - KH) // self.stride[0] + 1
        out_w = (W + 2 * self.padding[1] - KW) // self.stride[1] + 1

        x_unf = F.unfold(
            x,
            kernel_size=self.kernel_size,
            stride=self.stride,
            padding=self.padding,
        )  # (B, C*KH*KW, L)

        x_unf = x_unf.transpose(1, 2).contiguous()  # (B, L, C*KH*KW)
        w = self.weight.view(self.weight.size(0), -1).t().contiguous()  # (C*KH*KW, out_channels)

        outputs = []

        for b in range(B):
            if self.format == "int":
                # Quantize activations and weights
                A_q, A_scale = quantize_tensor(x_unf[b], self.bitwidth, dtype=torch.int32)
                B_q, B_scale = quantize_tensor(w, self.bitwidth, dtype=torch.int32)

                # Quantize bias to accumulator scale
                if self.bias is not None:
                    bias_q = quantize_bias(self.bias, A_scale, B_scale)
                    C_q = bias_q.unsqueeze(0).repeat(A_q.shape[0], 1)
                else:
                    C_q = torch.zeros(
                        (A_q.shape[0], w.shape[1]),
                        dtype=torch.int32,
                        device=A_q.device,
                    )

                A_np = A_q.detach().cpu().numpy().astype(np.int32)
                B_np = B_q.detach().cpu().numpy().astype(np.int32)
                C_np = C_q.detach().cpu().numpy().astype(np.int32)

                # Integer backend computes: A_q @ B_q + C_q
                D_q_np = self.backend.matmul(A_np, B_np, C_np)

                # Dequantize
                D = torch.from_numpy(D_q_np).to(x.device).float() * (A_scale * B_scale)

            else:
                A_np = x_unf[b].detach().cpu().numpy().astype(np.float32)
                B_np = w.detach().cpu().numpy().astype(np.float32)

                if self.bias is not None:
                    bias_np = self.bias.detach().cpu().numpy().astype(np.float32)
                    C_np = np.tile(bias_np, (A_np.shape[0], 1))
                else:
                    C_np = np.zeros((A_np.shape[0], w.shape[1]), dtype=np.float32)

                D_np = self.backend.matmul(A_np, B_np, C_np)
                D = torch.from_numpy(D_np).to(x.device).float()

            outputs.append(D)

        return (
            torch.stack(outputs)
            .permute(0, 2, 1)
            .contiguous()
            .view(B, self.weight.size(0), out_h, out_w)
        )
