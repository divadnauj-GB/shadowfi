import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
from pytorch.custom_backends import wrapper_backends


def replace_fp32_layers_with_rtl(
    model,
    backend_name: str,
    backend_layers=None,
    num_bits=8,
    backend=None,
    replaced=None,
    prefix="",
    format="int",
):
    """
    Recursively replace selected FP32 layers with RTL wrappers.

    Returns
    -------
    replaced : list[str]
        Full dotted names of modules that were replaced.
    """
    if replaced is None:
        replaced = []

    layer_map = {
        "conv2d": torch.nn.Conv2d,
        "linear": torch.nn.Linear,
    }
    backend_layers = backend_layers or []

    custom_wrappers = wrapper_backends.get(backend_name)
    if custom_wrappers is None:
        raise ValueError(
            f"Unknown backend: '{backend_name}'. "
            f"Available: {list(wrapper_backends.keys())}"
        )

    for child_name, child_mod in model.named_children():
        full_name = f"{prefix}{child_name}"
        replaced_here = False

        for key in backend_layers:
            layer_type = layer_map.get(key)
            wrapper_cls = custom_wrappers.get(key)
            if layer_type and wrapper_cls and isinstance(child_mod, layer_type):
                wrapped = wrapper_cls(
                    child_mod,
                    backend=backend,
                    bitwidth=num_bits,
                    layer_name=full_name,
                    format=format,
                )
                model._modules[child_name] = wrapped
                replaced.append(full_name)
                replaced_here = True
                break

        if not replaced_here:
            replace_fp32_layers_with_rtl(
                child_mod,
                backend_name,
                backend_layers,
                num_bits,
                backend,
                replaced,
                prefix=f"{full_name}.",
            )
    return replaced


def profile_model_layers(
    model, backend_layers=None, prefix="", layer_id=0, profile=None
):
    """
    Recursively profile layers in the model that match backend_layers.

    Returns
    -------
    profile : list of dicts
        Each dict contains: 'id', 'name', 'type'.
    """
    if profile is None:
        profile = []

    layer_map = {
        "conv2d": torch.nn.Conv2d,
        "linear": torch.nn.Linear,
        "attention": Attention,
    }
    backend_layers = backend_layers or []

    for child_name, child_mod in model.named_children():
        full_name = f"{prefix}{child_name}"
        for key in backend_layers:
            layer_type = layer_map.get(key)
            if layer_type and isinstance(child_mod, layer_type):
                profile.append({"id": layer_id, "name": full_name, "type": key})
                layer_id += 1
                break

        # Recurse into children
        profile, layer_id = profile_model_layers(
            child_mod,
            backend_layers,
            prefix=f"{full_name}.",
            layer_id=layer_id,
            profile=profile,
        )

    return profile, layer_id


def replace_layers_by_id(
    model,
    target_ids,
    backend_name,
    backend_layers=None,
    num_bits=8,
    backend=None,
    replaced=None,
    prefix="",
    current_id=0,
    format="int",
):
    """
    Recursively replace only the layers with IDs in target_ids.

    Returns
    -------
    replaced : list of str
        Full dotted names of modules replaced.
    """
    if replaced is None:
        replaced = []

    layer_map = {
        "conv2d": torch.nn.Conv2d,
        "linear": torch.nn.Linear,
        "attention": Attention,
    }
    backend_layers = backend_layers or []

    custom_wrappers = wrapper_backends.get(backend_name)
    if custom_wrappers is None:
        raise ValueError(f"Unknown backend: '{backend_name}'")

    for child_name, child_mod in model.named_children():
        full_name = f"{prefix}{child_name}"
        for key in backend_layers:
            layer_type = layer_map.get(key)
            wrapper_cls = custom_wrappers.get(key)
            if layer_type and wrapper_cls and isinstance(child_mod, layer_type):
                if current_id in target_ids:
                    wrapped = wrapper_cls(
                        child_mod,
                        backend=backend,
                        bitwidth=num_bits,
                        layer_name=full_name,
                        format=format,
                    )
                    model._modules[child_name] = wrapped
                    replaced.append(full_name)
                current_id += 1
                break
        else:
            # Recurse into children
            current_id = replace_layers_by_id(
                child_mod,
                target_ids,
                backend_name,
                backend_layers,
                num_bits,
                backend,
                replaced,
                prefix=f"{full_name}.",
                current_id=current_id,
            )

    return current_id
