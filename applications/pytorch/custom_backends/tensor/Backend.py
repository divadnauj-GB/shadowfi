import numpy as np


class TensorBackend:
    def __init__(self, bitwidth=8, format="int"):
        self.bitwidth = bitwidth
        self.format = format

    def matmul_fn(self, A, B, C):
        A = np.asarray(A)
        B = np.asarray(B)
        C = np.asarray(C)

        result = A @ B + C
        return result

    def matmul(self, A, B, C):
        return self.matmul_fn(A, B, C)
