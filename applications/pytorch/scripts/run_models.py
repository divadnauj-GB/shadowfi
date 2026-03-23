import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import torch
from omegaconf import OmegaConf

from pytorch.utils.dataloaders import DatasetLoader
from pytorch.utils.registry import get_model
from pytorch.utils.eval import evaluate_model
from pytorch.utils.logging_config import setup_logging


def main(config):
    log_level = config.logging.get("level", "INFO")
    log_file = config.logging.get("log_file", None)
    logger = setup_logging(log_file=log_file, level=log_level)

    device = torch.device("cpu")

    logger.info(f"Running on {device} device")

    # Load test data
    logger.info("Loading dataset...")
    data_loader = DatasetLoader(
        dataset_name=config.dataset.name,
        dataset_root=config.paths.dataset_root,
        batch_size_test=config.training.batch_size_test,
        normalize=config.dataset.normalize,
        download=config.dataset.get("download", True),
        train_resize=config.dataset.get("train_resize"),
        test_resize=config.dataset.get("test_resize"),
        test_center_crop=config.dataset.get("test_center_crop"),
        train_random_resized_crop=config.dataset.get("train_random_resized_crop"),
        train_horizontal_flip_prob=config.dataset.get(
            "train_horizontal_flip_prob", 0.0
        ),
    )
    dataset_num_classes = data_loader.num_classes
    dataset_input_channels = data_loader.input_channels
    dataset_image_size = data_loader.image_size
    _, test_loader = data_loader.get_loaders()
    logger.info(
        f"Dataset '{config.dataset.name}' loaded. Classes: {dataset_num_classes}"
    )

    # Load FP32 model
    logger.info(f"Initializing FP32 model: {config.model.name}")

    model_kwargs = OmegaConf.to_container(config.model, resolve=True)
    model_name = model_kwargs.pop("name")

    if (
        "num_classes" in model_kwargs
        and model_kwargs["num_classes"] != dataset_num_classes
    ):
        logger.warning(
            f"Model config's num_classes ({model_kwargs['num_classes']}) "
            f"does not match dataset's ({dataset_num_classes}). Using dataset's value."
        )
    model_kwargs["num_classes"] = dataset_num_classes

    if "input_channels" in model_kwargs:
        if (
            "in_chans" in model_kwargs
            and model_kwargs["in_chans"] != model_kwargs["input_channels"]
        ):
            logger.warning(
                f"Both 'input_channels' ({model_kwargs['input_channels']}) and 'in_chans' ({model_kwargs['in_chans']}) "
                f"are specified in model config. Using 'in_chans'."
            )
        else:
            model_kwargs["in_chans"] = model_kwargs.pop("input_channels")

    if "in_chans" not in model_kwargs:
        model_kwargs["in_chans"] = dataset_input_channels

    if "img_size" in model_kwargs and model_kwargs["img_size"] != dataset_image_size:
        logger.warning(
            f"Model config's img_size ({model_kwargs['img_size']}) "
            f"does not match dataset's ({dataset_image_size}). Using dataset's value."
        )
    model_kwargs["img_size"] = dataset_image_size

    model_fp32 = get_model(model_name, **model_kwargs)
    try:
        model_fp32.load_state_dict(
            torch.load(config.paths.model_fp32, map_location="cpu")
        )
    except FileNotFoundError:
        logger.error(f"❌ FP32 model weights not found at: {config.paths.model_fp32}")
        logger.error("Please ensure you have trained and saved the FP32 model first.")
        sys.exit(1)

    model_fp32.eval()
    evaluate_model(model_fp32, device, test_loader, desc="FP32")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str)
    args = parser.parse_args()

    config = OmegaConf.load(args.config)
    main(config)
