import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class DatasetLoader:
    _DATASET_INFO = {
        "mnist": {
            "dataset_class": datasets.MNIST,
            "mean": (0.1307,),
            "std": (0.3081,),
            "num_classes": 10,
            "input_channels": 1,
            "image_size": 28,
        },
        "fashionmnist": {
            "dataset_class": datasets.FashionMNIST,
            "mean": (0.2860,),
            "std": (0.3530,),
            "num_classes": 10,
            "input_channels": 1,
            "image_size": 28,
        },
        "cifar10": {
            "dataset_class": datasets.CIFAR10,
            "mean": (0.4914, 0.4822, 0.4465),
            "std": (0.2470, 0.2435, 0.2616),
            "num_classes": 10,
            "input_channels": 3,
            "image_size": 32,
        },
        "cifar100": {
            "dataset_class": datasets.CIFAR100,
            "mean": (0.5071, 0.4867, 0.4408),
            "std": (0.2675, 0.2565, 0.2761),
            "num_classes": 100,
            "input_channels": 3,
            "image_size": 32,
        },
        "imagenet": {
            "dataset_class": datasets.ImageNet,
            "mean": (0.485, 0.456, 0.406),
            "std": (0.229, 0.224, 0.225),
            "num_classes": 1000,
            "input_channels": 3,
            "image_size": 224,
        },
    }

    def __init__(
        self,
        dataset_name: str,
        dataset_root: str = "datasets",
        batch_size_train: int = 64,
        batch_size_test: int = 1000,
        normalize: bool = True,
        download: bool = True,
        train_resize: int = None,
        test_resize: int = None,
        test_center_crop: int = None,
        train_random_resized_crop: int = None,
        train_horizontal_flip_prob: float = 0.5,
        max_test_samples: int = None,
    ):
        self.dataset_name = dataset_name.lower()
        self.dataset_root = Path(dataset_root)
        self.batch_size_train = batch_size_train
        self.batch_size_test = batch_size_test
        self.download = download
        self.normalize = normalize

        if self.dataset_name not in self._DATASET_INFO:
            raise ValueError(
                f"Unsupported dataset: '{dataset_name}'. "
                f"Available datasets: {list(self._DATASET_INFO.keys())}"
            )

        self.dataset_info = self._DATASET_INFO[self.dataset_name]
        self.dataset_class = self.dataset_info["dataset_class"]

        self.num_classes = self.dataset_info["num_classes"]
        self.input_channels = self.dataset_info["input_channels"]
        self.image_size = self.dataset_info["image_size"]
        self.max_test_samples = max_test_samples

        self.train_transform = self._get_transforms(
            is_train=True,
            resize=train_resize,
            random_resized_crop=train_random_resized_crop,
            horizontal_flip_prob=train_horizontal_flip_prob,
        )
        self.test_transform = self._get_transforms(
            is_train=False,
            resize=test_resize,
            center_crop=test_center_crop,
        )

        self.dataset_root.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"DataLoader initialized for dataset '{self.dataset_name}' "
            f"with root '{self.dataset_root}'. "
            f"Input channels: {self.input_channels}, Num classes: {self.num_classes}."
        )

    def _get_transforms(
        self,
        is_train: bool,
        resize: int = None,
        random_resized_crop: int = None,
        center_crop: int = None,
        horizontal_flip_prob: float = 0.0,
    ):
        transform_list = []

        if is_train:
            if random_resized_crop:
                transform_list.append(transforms.RandomResizedCrop(random_resized_crop))
            elif resize:
                transform_list.append(transforms.Resize(resize))
            if horizontal_flip_prob > 0:
                transform_list.append(
                    transforms.RandomHorizontalFlip(horizontal_flip_prob)
                )

            if not random_resized_crop and not resize and self.image_size:
                transform_list.append(transforms.Resize(self.image_size))

        else:
            if center_crop:
                transform_list.append(
                    transforms.Resize(max(self.image_size, center_crop + 32))
                )
                transform_list.append(transforms.CenterCrop(center_crop))
            elif resize:
                transform_list.append(transforms.Resize(resize))

            if not center_crop and not resize and self.image_size:
                transform_list.append(transforms.Resize(self.image_size))

        transform_list.append(transforms.ToTensor())

        if self.normalize:
            transform_list.append(
                transforms.Normalize(
                    self.dataset_info["mean"], self.dataset_info["std"]
                )
            )

        logger.debug(f"{'Train' if is_train else 'Test'} Transforms: {transform_list}")
        return transforms.Compose(transform_list)

    def get_loaders(self):
        try:
            train_dataset = self.dataset_class(
                root=self.dataset_root,
                train=True,
                transform=self.train_transform,
                download=self.download,
            )
            train_loader = DataLoader(
                train_dataset,
                batch_size=self.batch_size_train,
                shuffle=True,
                num_workers=(
                    torch.cuda.device_count() * 4 if torch.cuda.is_available() else 4
                ),
            )
            logger.info(
                f"Train loader created for {self.dataset_name}. Samples: {len(train_dataset)}, Batches: {len(train_loader)}"
            )

            test_dataset_full = self.dataset_class(
                root=self.dataset_root,
                train=False,
                transform=self.test_transform,
                download=self.download,
            )

            if self.max_test_samples is not None and self.max_test_samples > 0:
                if self.max_test_samples < len(test_dataset_full):
                    # Crear un subconjunto de test_dataset
                    indices = list(range(self.max_test_samples))
                    test_dataset = Subset(test_dataset_full, indices)
                    logger.info(f"Limiting test set to {len(test_dataset)} samples.")
                else:
                    test_dataset = test_dataset_full
                    logger.info(
                        f"max_test_samples ({self.max_test_samples}) is greater than or equal to total test samples ({len(test_dataset_full)}). Using full test set."
                    )
            else:
                test_dataset = test_dataset_full

            test_loader = DataLoader(
                test_dataset,
                batch_size=self.batch_size_test,
                shuffle=False,
                num_workers=(
                    torch.cuda.device_count() * 4 if torch.cuda.is_available() else 4
                ),
            )
            logger.info(
                f"Test loader created for {self.dataset_name}. Samples: {len(test_dataset)}, Batches: {len(test_loader)}"
            )

        except Exception as e:
            logger.error(f"Failed to load dataset '{self.dataset_name}'. Error: {e}")
            logger.error(
                "Please ensure the dataset can be downloaded or exists at the specified root."
            )
            raise

        return train_loader, test_loader
