import numpy as np
import tcu_hw


def float_bits_matrix(x: np.ndarray) -> np.ndarray:
    return x.astype(np.float32).view(np.uint32)


def print_matrix(name: str, x: np.ndarray, precision: int = 8) -> None:
    print(name)
    for row in x:
        vals = " ".join(f"{float(v):.{precision}f}" for v in row)
        print(f"[ {vals} ]")
    print()


def print_bits(name: str, x: np.ndarray) -> None:
    bits = float_bits_matrix(x)
    print(name)
    for row in bits:
        vals = " ".join(f"0x{int(v):08x}" for v in row)
        print(f"[ {vals} ]")
    print()


def compare_matrices(hw: np.ndarray, sw: np.ndarray) -> None:
    print("Element-wise comparison")
    for i in range(hw.shape[0]):
        for j in range(hw.shape[1]):
            hb = int(float_bits_matrix(hw)[i, j])
            sb = int(float_bits_matrix(sw)[i, j])
            err = abs(float(hw[i, j]) - float(sw[i, j]))
            status = "[EXACT]" if hb == sb else "[DIFF]"
            print(
                f"({i},{j}) "
                f"hw={float(hw[i, j]):.8f} "
                f"sw={float(sw[i, j]):.8f} "
                f"abs_err={err:.8f} "
                f"hw_bits=0x{hb:08x} "
                f"sw_bits=0x{sb:08x} "
                f"{status}"
            )
    print()


def run_4x4_test() -> None:
    A = np.array([
        [0.1, -0.2, 0.3, 0.4],
        [0.5, 0.6, 0.7, -0.8],
        [0.9, 1.1, 1.2, 1.3],
        [1.4, -1.5, 1.6, -1.7],
    ], dtype=np.float32)

    B = np.array([
        [0.3, 0.2, 0.1, 0.0],
        [0.6, 0.5, 0.4, 0.3],
        [0.9, 0.8, 0.7, 0.6],
        [1.2, 1.1, 1.0, 0.9],
    ], dtype=np.float32)

    C = np.array([
        [-0.01, 0.02, 0.03, 0.04],
        [0.05, 0.06, 0.07, 0.08],
        [0.09, 0.10, 0.11, 0.12],
        [0.13, 0.14, 0.15, -0.16],
    ], dtype=np.float32)

    hw = tcu_hw.matmul_hw(A, B, C, tile_latency=12)
    sw = tcu_hw.matmul_ref(A, B, C)

    print("==== 4x4 TEST ====")
    print_matrix("A", A)
    print_matrix("B", B)
    print_matrix("C", C)
    print_matrix("HW", hw)
    print_matrix("REFERENCE", sw)

    print_bits("HW bits", hw)
    print_bits("REFERENCE bits", sw)

    compare_matrices(hw, sw)

    max_err = float(np.max(np.abs(hw - sw)))
    print(f"Max abs error: {max_err:.10f}")
    print()


def run_big_test() -> None:
    M, K, N = 9, 10, 11

    A = np.zeros((M, K), dtype=np.float32)
    B = np.zeros((K, N), dtype=np.float32)
    C = np.zeros((M, N), dtype=np.float32)

    for i in range(M):
        for j in range(K):
            sign = 1.0 if (i + j) % 2 == 0 else -1.0
            A[i, j] = np.float32(sign * (0.11 * (i + 1) + 0.07 * (j + 1)))

    for i in range(K):
        for j in range(N):
            sign = -1.0 if (i * 3 + j) % 3 == 0 else 1.0
            B[i, j] = np.float32(sign * (0.05 * (i + 1) + 0.09 * (j + 1)))

    for i in range(M):
        for j in range(N):
            C[i, j] = np.float32(0.013 * (i + 1) + 0.021 * (j + 1))

    hw = tcu_hw.matmul_hw(A, B, C, tile_latency=12)
    sw = tcu_hw.matmul_ref(A, B, C)

    print("==== BIG TEST (padding/cropping) ====")
    print(f"A shape: {A.shape}")
    print(f"B shape: {B.shape}")
    print(f"C shape: {C.shape}")
    print(f"HW shape: {hw.shape}")
    print(f"REF shape: {sw.shape}")

    max_err = float(np.max(np.abs(hw - sw)))
    print(f"Max abs error: {max_err:.10f}")

    tol = 1e-4
    print("RESULT:", "PASS" if max_err <= tol else "FAIL")
    print()


def main() -> None:
    print("Module doc:", tcu_hw.__doc__)
    run_4x4_test()
    run_big_test()


if __name__ == "__main__":
    main()
