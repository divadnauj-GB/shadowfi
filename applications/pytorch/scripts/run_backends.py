import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import argparse
from omegaconf import OmegaConf

from pytorch.utils.logging_config import setup_logging
from pytorch.utils.utils import get_device
from pytorch.utils.eval import evaluate_model

from utils import (
    load_fp32_model,
    get_test_loader
)

from utils_replace import replace_fp32_layers_with_rtl


def run_evaluation(config, logger, use_wrappers=True):
    device = get_device()
    logger.info(f"Using device: {device}")

    test_loader, num_classes, in_chans, img_size = get_test_loader(
        config,
        config.dataset,
        config.training,
    )

    if use_wrappers:
        logger.info("🧠 Loading FP32 model and applying RTL wrappers...")
        # Pass the entire config.model and dataset-derived params to load_fp32_model
        model = load_fp32_model(
            config.paths.model_fp32,
            config.model,
            num_classes,
            in_chans,
            img_size,
            device,
        )

        backend_cfg = config.get("backend", {})
        backend_name = backend_cfg.get("name", "none")
        backend_layers = backend_cfg.get("backend_layers", [])
        bitwidth = backend_cfg.get("bitwidth", 8)
        format = backend_cfg.get("format", "int")

        replace_fp32_layers_with_rtl(
            model,
            backend_name,
            backend_layers,
            bitwidth,
            backend_cfg,
            format=format
        )
    else:
        logger.info("🧠 Loading baseline FP32 model...")
        # Pass the entire config.model and dataset-derived params to load_fp32_model
        model = load_fp32_model(
            config.paths.model_fp32,
            config.model,
            num_classes,
            in_chans,
            img_size,
            device
        )

    desc = "RTL FP32 Evaluation" if use_wrappers else "Baseline FP32 Evaluation"
    logger.info("📏 Running evaluation...")
    return evaluate_model(model, device, test_loader, desc=desc)


def main(config):
    logger = setup_logging(
        log_file=config.logging.get("log_file", None),
        level=config.logging.get("level", "INFO"),
    )

    acc_baseline = run_evaluation(config, logger, use_wrappers=False)
    acc_wrapped = run_evaluation(config, logger, use_wrappers=True)

    logger.info(f"✅ Baseline Accuracy: {acc_baseline:.2f}%")
    logger.info(f"✅ RTL Accuracy: {acc_wrapped:.2f}%")
    logger.info(f"📉 Accuracy drop due to wrappers: {acc_baseline - acc_wrapped:.4f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to config YAML")
    args = parser.parse_args()

    config = OmegaConf.load(args.config)
    main(config)
