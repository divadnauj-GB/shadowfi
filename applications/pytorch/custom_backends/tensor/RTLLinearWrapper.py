import torch
import torch.nn as nn
import numpy as np

from .Backend import TensorBackend
from .utils import quantize_tensor, quantize_bias


class RTLLinearWrapper(nn.Module):
    def __init__(
        self,
        linear,
        backend=None,
        bitwidth=8,
        format="int",
        layer_name: str | None = None,
        fault_config=None,
        sr_length: int = 1534,
    ):
        super().__init__()
        self.in_features = linear.in_features
        self.out_features = linear.out_features
        self.weight = linear.weight
        self.bias = linear.bias
        self.bitwidth = bitwidth
        self.format = format
        self.layer_name = layer_name
        self.backend = TensorBackend(bitwidth, format,
                                     fault_config=fault_config,
                                     sr_length=sr_length)

        self._weight_t = self.weight.t().contiguous()

        if self.format == "float":
            self._weight_np = self._weight_t.detach().cpu().numpy().astype(np.float32)
            self._bias_np = (
                self.bias.detach().cpu().numpy().astype(np.float32)
                if self.bias is not None
                else None
            )
        else:
            self._weight_np = None
            self._bias_np = None

    def forward(self, x):
        if x.device.type != "cpu":
            x = x.cpu()

        orig_shape = x.shape
        x_2d = x.reshape(-1, x.shape[-1])

        if self.format == "int":
            A_q, A_scale = quantize_tensor(x_2d, self.bitwidth, dtype=torch.int32)
            B_q, B_scale = quantize_tensor(self._weight_t, self.bitwidth, dtype=torch.int32)

            if self.bias is not None:
                bias_q = quantize_bias(self.bias, A_scale, B_scale)
                C_q = bias_q.unsqueeze(0).repeat(A_q.shape[0], 1)
            else:
                C_q = torch.zeros(
                    (A_q.shape[0], self.out_features),
                    dtype=torch.int32,
                    device=A_q.device,
                )

            A_np = A_q.detach().cpu().numpy().astype(np.int32)
            B_np = B_q.detach().cpu().numpy().astype(np.int32)
            C_np = C_q.detach().cpu().numpy().astype(np.int32)

            D_q_np = self.backend.matmul(A_np, B_np, C_np)
            D = torch.from_numpy(D_q_np).float() * (A_scale * B_scale)

        else:
            A_np = x_2d.detach().cpu().numpy().astype(np.float32)
            B_np = self._weight_np

            if self._bias_np is not None:
                C_np = np.tile(self._bias_np, (A_np.shape[0], 1))
            else:
                C_np = np.zeros((A_np.shape[0], self.out_features), dtype=np.float32)

            D_np = self.backend.matmul(A_np, B_np, C_np)
            D = torch.from_numpy(D_np).float()

        output = D.reshape(*orig_shape[:-1], self.out_features)
        return output
