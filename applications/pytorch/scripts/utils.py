import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
from omegaconf import DictConfig, ListConfig, OmegaConf

from pytorch.utils.dataloaders import DatasetLoader
from pytorch.utils.registry import get_model


def load_fp32_model(model_path, model_config, num_classes, in_chans, img_size, device):
    model_kwargs = OmegaConf.to_container(model_config, resolve=True)
    model_name = model_kwargs.pop("name")

    model_kwargs["num_classes"] = num_classes
    model_kwargs["in_chans"] = in_chans
    model_kwargs["img_size"] = img_size

    model = get_model(model_name, **model_kwargs)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model


def get_test_loader(main_config, dataset_config, training_config):
    data_loader = DatasetLoader(
        dataset_name=dataset_config.get("name"),
        dataset_root=main_config.paths.get("dataset_root"),
        batch_size_train=training_config.get("batch_size_train", 1),
        batch_size_test=training_config.get("batch_size_test", 1),
        normalize=dataset_config.get("normalize", False),
        download=dataset_config.get("download", True),
        train_resize=dataset_config.get("train_resize"),
        test_resize=dataset_config.get("test_resize"),
        test_center_crop=dataset_config.get("test_center_crop"),
        train_random_resized_crop=dataset_config.get("train_random_resized_crop"),
        train_horizontal_flip_prob=dataset_config.get("train_horizontal_flip_prob", 0.0),
        max_test_samples=dataset_config.get("max_test_samples", None),
        num_workers_train=training_config.get("num_workers_train", 4),
        num_workers_test=training_config.get("num_workers_test", 0),
        pin_memory=training_config.get("pin_memory", False),
        persistent_workers=training_config.get("persistent_workers", False),
    )
    _, test_loader = data_loader.get_loaders()

    return (
        test_loader,
        data_loader.num_classes,
        data_loader.input_channels,
        data_loader.image_size,
    )
