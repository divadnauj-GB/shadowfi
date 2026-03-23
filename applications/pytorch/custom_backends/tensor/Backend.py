import numpy as np
import tcu_hw


class TensorBackend:
    def __init__(self, bitwidth=8, format="float", tile_latency=12, persistent_core=True):
        self.bitwidth = bitwidth
        self.format = format
        self.tile_latency = tile_latency
        self.persistent_core = persistent_core
        self._core = tcu_hw.TcuHardware(tile_latency=tile_latency) if persistent_core else None

    def matmul_fn(self, A, B, C):
        if self.format == "float":
            A = np.asarray(A, dtype=np.float32)
            B = np.asarray(B, dtype=np.float32)
            C = np.asarray(C, dtype=np.float32)
        elif self.format == "int":
            A = np.asarray(A, dtype=np.int32)
            B = np.asarray(B, dtype=np.int32)
            C = np.asarray(C, dtype=np.int32)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

        if A.ndim != 2 or B.ndim != 2 or C.ndim != 2:
            raise ValueError("A, B, and C must be 2D matrices")

        if A.shape[1] != B.shape[0]:
            raise ValueError(f"Incompatible shapes for matmul: A{A.shape} and B{B.shape}")

        expected_c_shape = (A.shape[0], B.shape[1])
        if C.shape != expected_c_shape:
            raise ValueError(f"C must have shape {expected_c_shape}, but got {C.shape}")

        if self.format == "float":
            if self._core is not None:
                return self._core.matmul(A, B, C)
            return tcu_hw.matmul_hw(A, B, C, tile_latency=self.tile_latency)

        if self.format == "int":
            return A @ B + C

        raise ValueError(f"Unsupported format: {self.format}")

    def matmul(self, A, B, C):
        return self.matmul_fn(A, B, C)
