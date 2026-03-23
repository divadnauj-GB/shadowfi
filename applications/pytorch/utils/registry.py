import logging
from pytorch.models import LeNet, VGG11

logger = logging.getLogger("qtorchlab")


def get_model(name: str, **kwargs):
    """
    Retrieves a model instance by name, with the specified number of output classes.
    """
    model_name_lower = name.lower()

    if model_name_lower == "lenet":
        # Pass in_channels and input_spatial_size to LeNet
        return LeNet(**kwargs)
    elif model_name_lower == "vgg11":
        # Pass in_channels to VGG11
        return VGG11(**kwargs)
    else:
        logger.error(
            f"❌ Unknown model: '{name}'. Available models: alexnet, lenet, vgg11, ResNet18, vit_tiny."
        )
        raise ValueError(f"❌ Unknown model: '{name}'")
