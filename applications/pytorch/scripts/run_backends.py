import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import argparse
import torch
import tcu_hw
from omegaconf import OmegaConf

from pytorch.utils.logging_config import setup_logging
from pytorch.utils.utils import get_device
from pytorch.utils.eval import evaluate_model

from utils import load_fp32_model, get_test_loader
from utils_replace import replace_fp32_layers_with_rtl


# ---------------------------------------------------------------------------
# Fault configuration builder
# ---------------------------------------------------------------------------

def build_fault_config(fi_cfg) -> "tcu_hw.FaultConfig":
    """Build a tcu_hw.FaultConfig from the fault_injection config section.

    Supports two ways to specify target_nodes in the YAML:

      target_nodes: [1500, 1501, 1502]          # explicit list
      target_nodes_range: [1500, 1531]           # inclusive [start, end]

    If neither is present, all sr_nodes are targeted.
    """
    mode_map = {
        "STUCK_AT_0": tcu_hw.FaultMode.STUCK_AT_0,
        "STUCK_AT_1": tcu_hw.FaultMode.STUCK_AT_1,
        "BIT_FLIP":   tcu_hw.FaultMode.BIT_FLIP,
    }

    mode_str = fi_cfg.get("mode", "STUCK_AT_0").upper()
    if mode_str not in mode_map:
        raise ValueError(
            f"Unknown fault mode '{mode_str}'. "
            f"Valid options: {list(mode_map.keys())}"
        )
    mode = mode_map[mode_str]

    sr_length   = int(fi_cfg.get("sr_length", 1534))
    fault_cycle = int(fi_cfg.get("fault_cycle", 6))
    sr_nodes    = sr_length - 2  # last 2 bits are ctrl

    # Resolve target_nodes
    if "target_nodes" in fi_cfg and fi_cfg.target_nodes is not None:
        nodes = list(fi_cfg.target_nodes)
    elif "target_nodes_range" in fi_cfg and fi_cfg.target_nodes_range is not None:
        r = fi_cfg.target_nodes_range
        nodes = list(range(int(r[0]), int(r[1]) + 1))
    else:
        nodes = list(range(sr_nodes))  # all nodes

    cfg = tcu_hw.FaultConfig()
    cfg.mode         = mode
    cfg.target_nodes = nodes
    cfg.fault_cycle  = fault_cycle
    return cfg


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------

def run_evaluation(
    config,
    logger,
    test_loader,
    num_classes,
    in_chans,
    img_size,
    use_wrappers: bool = True,
    fault_config=None,
):
    """Load and evaluate the model under one of three modes:

    use_wrappers=False               → baseline FP32 (no RTL simulation)
    use_wrappers=True, fault=None    → golden RTL (hardware simulation, no fault)
    use_wrappers=True, fault=<cfg>   → FI RTL (hardware simulation with fault)
    """
    if use_wrappers:
        device = torch.device("cpu")
        logger.info("Using CPU (RTL simulation runs on CPU).")
    else:
        device = get_device()
        logger.info(f"Using device: {device}")

    model = load_fp32_model(
        config.paths.model_fp32,
        config.model,
        num_classes,
        in_chans,
        img_size,
        device,
    )

    if use_wrappers:
        backend_cfg   = config.get("backend", {})
        backend_name  = backend_cfg.get("name", "none")
        backend_layers = backend_cfg.get("backend_layers", [])
        bitwidth      = backend_cfg.get("bitwidth", 8)
        fmt           = backend_cfg.get("format", "int")
        sr_length     = int(config.get("fault_injection", {}).get("sr_length", 1534))

        if fault_config is not None and fmt != "float":
            logger.warning(
                "Fault injection is only supported with format='float'. "
                f"Current format='{fmt}' — FI will have no effect."
            )

        replaced = replace_fp32_layers_with_rtl(
            model,
            backend_name,
            backend_layers,
            bitwidth,
            backend_cfg,
            format=fmt,
            fault_config=fault_config,
            sr_length=sr_length,
        )

        if fault_config is not None:
            logger.info(
                f"FI active — mode={fault_config.mode.name}  "
                f"nodes={len(fault_config.target_nodes)}  "
                f"fault_cycle={fault_config.fault_cycle}"
            )
        logger.info(f"Replaced layers ({len(replaced)}): {replaced}")

    if fault_config is not None:
        desc = "FI RTL Evaluation"
    elif use_wrappers:
        desc = "Golden RTL Evaluation"
    else:
        desc = "Baseline FP32 Evaluation"

    logger.info(f"Running: {desc}")
    return evaluate_model(model, device, test_loader, desc=desc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(config):
    logger = setup_logging(
        log_file=config.logging.get("log_file", None),
        level=config.logging.get("level", "INFO"),
    )

    test_loader, num_classes, in_chans, img_size = get_test_loader(
        config,
        config.dataset,
        config.training,
    )

    # 1. Baseline FP32 — no hardware simulation
    logger.info("=" * 60)
    logger.info("PASS 1 — Baseline FP32")
    acc_baseline = run_evaluation(
        config, logger, test_loader, num_classes, in_chans, img_size,
        use_wrappers=False,
    )

    # 2. Golden RTL — hardware simulation, no fault
    logger.info("=" * 60)
    logger.info("PASS 2 — Golden RTL (no fault)")
    acc_golden = run_evaluation(
        config, logger, test_loader, num_classes, in_chans, img_size,
        use_wrappers=True,
        fault_config=None,
    )

    # 3. FI RTL — hardware simulation with fault injection (optional)
    fi_cfg = config.get("fault_injection", None)
    fi_enabled = fi_cfg is not None and fi_cfg.get("enabled", False)

    acc_fi = None
    fault_config = None
    if fi_enabled:
        logger.info("=" * 60)
        logger.info("PASS 3 — FI RTL (fault injection active)")
        fault_config = build_fault_config(fi_cfg)
        acc_fi = run_evaluation(
            config, logger, test_loader, num_classes, in_chans, img_size,
            use_wrappers=True,
            fault_config=fault_config,
        )

    # Summary
    logger.info("=" * 60)
    logger.info("RESULTS")
    logger.info(f"  Baseline FP32 accuracy : {acc_baseline:.4f}%")
    logger.info(f"  Golden RTL accuracy    : {acc_golden:.4f}%")
    logger.info(f"  RTL vs Baseline drop   : {acc_baseline - acc_golden:.4f}%")

    if acc_fi is not None:
        logger.info(f"  FI RTL accuracy        : {acc_fi:.4f}%")
        logger.info(f"  FI vs Baseline drop    : {acc_baseline - acc_fi:.4f}%")
        logger.info(f"  FI vs Golden drop      : {acc_golden - acc_fi:.4f}%")
        logger.info(
            f"  FI config — mode={fault_config.mode.name}  "
            f"nodes={len(fault_config.target_nodes)}  "
            f"fault_cycle={fault_config.fault_cycle}"
        )
    else:
        logger.info("  FI evaluation skipped (fault_injection.enabled: false)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate a model under baseline, golden RTL, and FI RTL modes."
    )
    parser.add_argument("--config", type=str, required=True,
                        help="Path to config YAML")
    args = parser.parse_args()

    config = OmegaConf.load(args.config)
    main(config)
