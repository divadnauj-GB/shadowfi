import numpy as np
import tcu_hw as tcu_fi_hw  # FI types now live in tcu_hw


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def max_abs_err(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        return float("inf")
    return float(np.max(np.abs(a - b)))


def fault_obs(fi: np.ndarray, golden: np.ndarray) -> bool:
    """True if fi result differs from golden (NaN/inf aware)."""
    if not np.isfinite(fi).all() or not np.isfinite(golden).all():
        return not np.array_equal(np.isnan(fi), np.isnan(golden)) or \
               not np.array_equal(np.isinf(fi), np.isinf(golden))
    return not np.array_equal(fi, golden)


def run_test(hw, A, B, C, hw_golden, cfg, name):
    fi_result = hw.matmul_fi(A, B, C, cfg)
    err = max_abs_err(fi_result, hw_golden)
    obs = fault_obs(fi_result, hw_golden)
    w00_hw = float(hw_golden[0, 0])
    w00_fi = float(fi_result[0, 0])
    print(f"  {name}")
    print(f"    Mode          : {cfg.mode}")
    print(f"    Nodes         : {len(cfg.target_nodes)}")
    if cfg.mode == tcu_fi_hw.FaultMode.BIT_FLIP:
        print(f"    Fault cycle   : {cfg.fault_cycle}")
    print(f"    Max err vs HW : {err:.6e}")
    print(f"    W[0][0] hw={w00_hw:.6f}  fi={w00_fi:.6f}")
    print(f"    Fault obs.    : {'YES' if obs else 'NO — masked'}")
    print()
    return fi_result, obs


# ---------------------------------------------------------------------------
# Shared inputs
# ---------------------------------------------------------------------------

A = np.array([
    [1.0,  2.0,  3.0,  4.0],
    [5.0,  6.0,  7.0,  8.0],
    [9.0,  10.0, 11.0, 12.0],
    [13.0, 14.0, 15.0, 16.0],
], dtype=np.float32)

B = np.array([
    [0.1, 0.2, 0.3, 0.4],
    [0.5, 0.6, 0.7, 0.8],
    [0.9, 1.0, 1.1, 1.2],
    [1.3, 1.4, 1.5, 1.6],
], dtype=np.float32)

C = np.array([
    [0.01, 0.02, 0.03, 0.04],
    [0.05, 0.06, 0.07, 0.08],
    [0.09, 0.10, 0.11, 0.12],
    [0.13, 0.14, 0.15, 0.16],
], dtype=np.float32)

print("=== TCU FI Python Testbench ===\n")
print(f"Module: {tcu_fi_hw.__doc__}\n")

hw = tcu_fi_hw.TcuFiHardware(sr_length=1534, tile_latency=12)
print(f"HW created: sr_length={hw.sr_length}  sr_nodes={hw.sr_nodes}  tile_latency={hw.tile_latency}\n")

# ---------------------------------------------------------------------------
# Test 0 — Baseline: FI model golden (no fault)
# ---------------------------------------------------------------------------
print("[Test 0] Golden baseline (no fault)")
hw_golden = hw.matmul(A, B, C)
sw_ref    = tcu_fi_hw.matmul_ref(A, B, C)
err0 = max_abs_err(hw_golden, sw_ref)
print(f"  HW golden vs SW ref: {err0:.6e}  {'PASS' if err0 <= 1e-4 else 'FAIL'}\n")

# ---------------------------------------------------------------------------
# Test 1 — Stuck-at-0, node 0 only
# ---------------------------------------------------------------------------
print("[Test 1] Stuck-at-0 (node 0 only)")
cfg1 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.STUCK_AT_0, [0], 6)
run_test(hw, A, B, C, hw_golden, cfg1, "SA0 node 0")

# ---------------------------------------------------------------------------
# Test 2 — Stuck-at-1, node 0 only
# ---------------------------------------------------------------------------
print("[Test 2] Stuck-at-1 (node 0 only)")
cfg2 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.STUCK_AT_1, [0], 6)
run_test(hw, A, B, C, hw_golden, cfg2, "SA1 node 0")

# ---------------------------------------------------------------------------
# Test 3 — Stuck-at-0, nodes 1500..1531 (observable)
# ---------------------------------------------------------------------------
print("[Test 3] Stuck-at-0 (nodes 1500..1531)")
cfg3 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.STUCK_AT_0, list(range(1500, 1532)), 6)
run_test(hw, A, B, C, hw_golden, cfg3, "SA0 nodes 1500-1531")

# ---------------------------------------------------------------------------
# Test 4 — Stuck-at-1, all nodes
# ---------------------------------------------------------------------------
print("[Test 4] Stuck-at-1 (all nodes)")
cfg4 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.STUCK_AT_1, list(range(hw.sr_nodes)), 6)
run_test(hw, A, B, C, hw_golden, cfg4, "SA1 all nodes")

# ---------------------------------------------------------------------------
# Test 5 — Bit-flip cycle 6, nodes 1000..1100 (observable)
# ---------------------------------------------------------------------------
print("[Test 5] Bit-flip at cycle 6 (nodes 1000..1100)")
cfg5 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.BIT_FLIP, list(range(1000, 1101)), 6)
run_test(hw, A, B, C, hw_golden, cfg5, "BF cycle 6, nodes 1000-1100")

# ---------------------------------------------------------------------------
# Test 6 — Manual control: fi_configure + fi_arm + matmul + fi_disarm
# ---------------------------------------------------------------------------
print("[Test 6] Manual FI control (SA0 nodes 1500-1531)")
cfg6 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.STUCK_AT_0, list(range(1500, 1532)), 6)
hw.fi_configure(cfg6)
hw.fi_arm()
manual_result = hw.matmul(A, B, C)   # runs with fault active
hw.fi_disarm()

auto_result, _ = run_test(hw, A, B, C, hw_golden, cfg6, "SA0 1500-1531 via matmul_fi")

manual_matches_auto = np.array_equal(manual_result, auto_result)
print(f"  Manual == automated: {'YES (PASS)' if manual_matches_auto else 'NO (FAIL)'}\n")

# ---------------------------------------------------------------------------
# Test 7 — Determinism: two identical FI runs
# ---------------------------------------------------------------------------
print("[Test 7] Determinism — two consecutive FI runs")
cfg7 = tcu_fi_hw.FaultConfig(tcu_fi_hw.FaultMode.STUCK_AT_0, list(range(1500, 1504)), 6)
r7a = hw.matmul_fi(A, B, C, cfg7)
r7b = hw.matmul_fi(A, B, C, cfg7)
print(f"  Identical results: {'YES (PASS)' if np.array_equal(r7a, r7b) else 'NO (FAIL)'}\n")

# ---------------------------------------------------------------------------
# Test 8 — FaultConfig repr and attribute mutation from Python
# ---------------------------------------------------------------------------
print("[Test 8] FaultConfig Python API")
cfg8 = tcu_fi_hw.FaultConfig()
cfg8.mode = tcu_fi_hw.FaultMode.BIT_FLIP
cfg8.target_nodes = list(range(1000, 1101))
cfg8.fault_cycle = 3
print(f"  cfg repr : {repr(cfg8)}")
r8 = hw.matmul_fi(A, B, C, cfg8)
obs8 = fault_obs(r8, hw_golden)
print(f"  BF cycle 3, nodes 1000-1100 fault obs.: {'YES' if obs8 else 'NO — masked'}\n")

# ---------------------------------------------------------------------------
# Test 9 — Stateless module-level function
# ---------------------------------------------------------------------------
print("[Test 9] Stateless matmul_fi_hw()")
r9 = tcu_fi_hw.matmul_fi_hw(A, B, C, cfg3)
obs9 = fault_obs(r9, hw_golden)
print(f"  SA0 nodes 1500-1531 fault obs.: {'YES' if obs9 else 'NO — masked'}\n")

print("=== Done ===")
