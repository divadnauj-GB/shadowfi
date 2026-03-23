import torch
import logging
from tqdm import tqdm


logger = logging.getLogger("qtorchlab")


def evaluate_model(model, device, test_loader, desc="Test"):
    """
    Evaluates the model on the test set and logs the accuracy.

    Args:
        model (torch.nn.Module): The model to evaluate.
        device (torch.device): The device to run evaluation on.
        test_loader (torch.utils.data.DataLoader): DataLoader for the test set.
        desc (str): Description for the evaluation phase (e.g., "FP32", "INT8").

    Returns:
        float: The calculated accuracy.
    """
    try:
        model.eval()
    except AttributeError:
        logger.warning(
            "⚠️ Loaded quantized model does not require .eval() or it's already applied."
        )

    correct = total = 0
    eval_bar = tqdm(test_loader, desc=f"{desc} Evaluation", leave=False, unit="batch")

    with torch.no_grad():
        for data, target in eval_bar:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)

            # Update progress bar with current accuracy
            eval_bar.set_postfix(accuracy=f"{100. * correct / total:.2f}%")

    acc = 100.0 * correct / total
    logger.info(f"📊 {desc} Accuracy: {acc:.2f}% (Correct: {correct}/{total})")
    return acc
