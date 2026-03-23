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
        num_workers_train: int | None = None,
        num_workers_test: int | None = 0,
        pin_memory: bool = False,
        persistent_workers: bool = False,
    ):
        self.dataset_name = dataset_name.lower()
        self.dataset_root = Path(dataset_root)
        self.batch_size_train = batch_size_train
        self.batch_size_test = batch_size_test
        self.download = download
        self.normalize = normalize
        self.max_test_samples = max_test_samples

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

        if num_workers_train is None:
            self.num_workers_train = 4
        else:
            self.num_workers_train = num_workers_train

        if num_workers_test is None:
            self.num_workers_test = 0
        else:
            self.num_workers_test = num_workers_test

        self.pin_memory = pin_memory
        self.persistent_workers = persistent_workers

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
        logger.info(
            f"Loader settings -> "
            f"train_workers: {self.num_workers_train}, "
            f"test_workers: {self.num_workers_test}, "
            f"pin_memory: {self.pin_memory}, "
            f"persistent_workers: {self.persistent_workers}"
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

    def _loader_kwargs(self, is_train: bool) -> dict:
        num_workers = self.num_workers_train if is_train else self.num_workers_test

        kwargs = {
            "num_workers": num_workers,
            "pin_memory": self.pin_memory,
        }

        if num_workers > 0:
            kwargs["persistent_workers"] = self.persistent_workers

        return kwargs

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
                **self._loader_kwargs(is_train=True),
            )

            logger.info(
                f"Train loader created for {self.dataset_name}. "
                f"Samples: {len(train_dataset)}, Batches: {len(train_loader)}"
            )

            test_dataset_full = self.dataset_class(
                root=self.dataset_root,
                train=False,
                transform=self.test_transform,
                download=self.download,
            )

            if self.max_test_samples is not None and self.max_test_samples > 0:
                if self.max_test_samples < len(test_dataset_full):
                    indices = list(range(self.max_test_samples))
                    test_dataset = Subset(test_dataset_full, indices)
                    logger.info(f"Limiting test set to {len(test_dataset)} samples.")
                else:
                    test_dataset = test_dataset_full
                    logger.info(
                        f"max_test_samples ({self.max_test_samples}) is greater than or equal to "
                        f"total test samples ({len(test_dataset_full)}). Using full test set."
                    )
            else:
                test_dataset = test_dataset_full

            test_loader = DataLoader(
                test_dataset,
                batch_size=self.batch_size_test,
                shuffle=False,
                **self._loader_kwargs(is_train=False),
            )

            logger.info(
                f"Test loader created for {self.dataset_name}. "
                f"Samples: {len(test_dataset)}, Batches: {len(test_loader)}"
            )

        except Exception as e:
            logger.error(f"Failed to load dataset '{self.dataset_name}'. Error: {e}")
            logger.error(
                "Please ensure the dataset can be downloaded or exists at the specified root."
            )
            raise

        return train_loader, test_loader
