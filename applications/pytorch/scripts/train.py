import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import torch
import torch.nn as nn
import torch.optim as optim
from omegaconf import OmegaConf

from pytorch.utils.dataloaders import DatasetLoader
from pytorch.utils.utils import get_device, ensure_dir, test, train
from pytorch.utils.registry import get_model
from pytorch.utils.logging_config import setup_logging


def main(config):
    # Setup logging as defined in the config
    log_level = config.logging.get("level", "INFO")
    log_file = config.logging.get("log_file", None)
    logger = setup_logging(log_file=log_file, level=log_level)

    logger.info("--- Starting Model Training Process ---")
    logger.info(f"Using configuration from: {args.config}")

    # Determine the device (CPU/GPU)
    device = get_device()
    logger.info(f"Running on {device} device")

    logger.info("Loading dataset...")
    # Instantiate DatasetLoader with all relevant parameters from config.dataset
    # Use .get() for optional parameters, providing default values where appropriate
    data_loader = DatasetLoader(
        dataset_name=config.dataset.name,
        dataset_root=config.paths.dataset_root,
        normalize=config.dataset.normalize,
        batch_size_train=config.training.batch_size_train,
        batch_size_test=config.training.batch_size_test,
        download=config.dataset.get(
            "download", True
        ),  # Allow controlling download from config
        # Pass dataset-specific transform parameters
        train_resize=config.dataset.get("train_resize"),
        test_resize=config.dataset.get("test_resize"),
        test_center_crop=config.dataset.get("test_center_crop"),
        train_random_resized_crop=config.dataset.get("train_random_resized_crop"),
        train_horizontal_flip_prob=config.dataset.get(
            "train_horizontal_flip_prob", 0.5
        ),  # Default to 0.5
    )

    # Retrieve dataset properties from the data_loader
    dataset_num_classes = data_loader.num_classes
    dataset_input_channels = data_loader.input_channels
    dataset_image_size = data_loader.image_size  # Important for ViTs/ResNets

    # Get the actual data loaders
    train_loader, test_loader = data_loader.get_loaders()

    logger.info(
        f"Dataset '{config.dataset.name}' loaded. "
        f"Classes: {dataset_num_classes}, "
        f"Input Channels: {dataset_input_channels}, "
        f"Image Size: {dataset_image_size}x{dataset_image_size}"
    )

    logger.info(f"Initializing model: {config.model.name}")

    # Create a dictionary for model constructor arguments
    # Start with a copy of all parameters from config.model
    # OmegaConf.to_container converts it to a standard Python dict.
    model_kwargs = OmegaConf.to_container(config.model, resolve=True)

    # Remove 'name' as it's passed separately to get_model
    model_name = model_kwargs.pop("name")

    # Override/set crucial parameters based on the dataset properties
    # These are usually fundamental to the model's first layer and output layer

    # 1. num_classes: Should always match the dataset
    if (
        "num_classes" in model_kwargs
        and model_kwargs["num_classes"] != dataset_num_classes
    ):
        logger.warning(
            f"Model config's num_classes ({model_kwargs['num_classes']}) "
            f"does not match dataset's ({dataset_num_classes}). Using dataset's value."
        )
    model_kwargs["num_classes"] = dataset_num_classes

    # 2. Input Channels: Standardize on 'in_chans' and prioritize dataset
    if "input_channels" in model_kwargs:  # Handle older 'input_channels' naming
        if (
            "in_chans" in model_kwargs
            and model_kwargs["in_chans"] != model_kwargs["input_channels"]
        ):
            logger.warning(
                f"Both 'input_channels' ({model_kwargs['input_channels']}) and 'in_chans' ({model_kwargs['in_chans']}) "
                f"are specified in model config. Using 'in_chans'."
            )
        else:
            model_kwargs["in_chans"] = model_kwargs.pop(
                "input_channels"
            )  # Convert to 'in_chans'

    if "in_chans" not in model_kwargs:  # If still not set, use dataset's
        model_kwargs["in_chans"] = dataset_input_channels

    # 3. Image Size: Use 'img_size' and prioritize dataset
    if "img_size" in model_kwargs and model_kwargs["img_size"] != dataset_image_size:
        logger.warning(
            f"Model config's img_size ({model_kwargs['img_size']}) "
            f"does not match dataset's ({dataset_image_size}). Using dataset's value."
        )
    model_kwargs["img_size"] = dataset_image_size

    # Pass all collected keyword arguments to get_model
    # Any other parameters in config.model (e.g., patch_size, embed_dim for ViT)
    # will be passed directly as kwargs.
    model = get_model(model_name, **model_kwargs).to(device)
    logger.info(f"Model {model_name} initialized with parameters: {model_kwargs}")

    optimizer = optim.Adam(model.parameters(), lr=config.training.lr)
    criterion = nn.CrossEntropyLoss()

    logger.info(f"Starting model training for {config.training.epochs} epochs...")
    train(
        model, device, train_loader, optimizer, criterion, epochs=config.training.epochs
    )
    logger.info("Training finished.")

    logger.info("Evaluating final FP32 model...")
    acc = test(model, device, test_loader, desc="FP32")
    logger.info(f"📈 Final Accuracy: {acc['accuracy']:.2f}%")

    # Ensure the save directory exists and save the model
    save_path = Path(config.paths.model_fp32)
    ensure_dir(save_path)  # This ensures the parent directories for the file exist
    torch.save(model.state_dict(), save_path)
    logger.info(f"💾 Saved FP32 model to: {save_path}")
    logger.info("--- Model Training Process Completed ---")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Train a CNN or Vision Transformer model."
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the model and training configuration YAML file (e.g., configs/vit_tiny.yaml)",
    )
    args = parser.parse_args()

    # Load the configuration using OmegaConf
    config = OmegaConf.load(args.config)

    # Run the main training function
    main(config)
