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

        # Static weight layout for GEMM path
        self._weight_2d_torch = self.weight.view(self.weight.size(0), -1).t().contiguous()
        self.out_channels = self.weight.size(0)

        # Float caches
        self._weight_np = None
        self._bias_np = None

        # Int caches
        self._weight_q_np = None
        self._weight_scale = None
        self._bias_q_np = None

        self._build_caches()

    def _build_caches(self):
        if self.format == "float":
            self._weight_np = self._weight_2d_torch.detach().cpu().numpy().astype(np.float32)
            self._bias_np = (
                self.bias.detach().cpu().numpy().astype(np.float32)
                if self.bias is not None
                else None
            )

        elif self.format == "int":
            weight_q, weight_scale = quantize_tensor(
                self._weight_2d_torch,
                self.bitwidth,
                dtype=torch.int32,
            )
            self._weight_q_np = weight_q.detach().cpu().numpy().astype(np.int32)
            self._weight_scale = float(weight_scale)

            if self.bias is not None:
                bias_q = quantize_bias(self.bias, 1.0, self._weight_scale)
                self._bias_q_np = bias_q.detach().cpu().numpy().astype(np.int32)
            else:
                self._bias_q_np = None

    def forward(self, x):
        if x.device.type != "cpu":
            x = x.cpu()

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

        x_unf = x_unf.transpose(1, 2).contiguous()  # (B, L, K)
        Bsz, L, Kdim = x_unf.shape

        if self.format == "float":
            A_np = x_unf.reshape(Bsz * L, Kdim).detach().cpu().numpy().astype(np.float32)
            B_np = self._weight_np

            if self._bias_np is not None:
                C_np = np.broadcast_to(self._bias_np, (A_np.shape[0], self.out_channels)).copy()
            else:
                C_np = np.zeros((A_np.shape[0], self.out_channels), dtype=np.float32)

            D_np = self.backend.matmul(A_np, B_np, C_np)
            D = torch.from_numpy(D_np).float().reshape(Bsz, L, self.out_channels)

        elif self.format == "int":
            x_2d = x_unf.reshape(Bsz * L, Kdim)

            A_q, A_scale = quantize_tensor(x_2d, self.bitwidth, dtype=torch.int32)

            # Cached quantized weights
            B_np = self._weight_q_np
            B_scale = self._weight_scale

            if self.bias is not None:
                bias_q = quantize_bias(self.bias, A_scale, B_scale)
                C_q = bias_q.unsqueeze(0).repeat(A_q.shape[0], 1)
            else:
                C_q = torch.zeros(
                    (A_q.shape[0], self.out_channels),
                    dtype=torch.int32,
                    device=A_q.device,
                )

            A_np = A_q.detach().cpu().numpy().astype(np.int32)
            C_np = C_q.detach().cpu().numpy().astype(np.int32)

            D_q_np = self.backend.matmul(A_np, B_np, C_np)
            D = torch.from_numpy(D_q_np).float() * (A_scale * B_scale)
            D = D.reshape(Bsz, L, self.out_channels)

        else:
            raise ValueError(f"Unsupported format: {self.format}")

        return (
            D.permute(0, 2, 1)
            .contiguous()
            .view(Bsz, self.out_channels, out_h, out_w)
        )
