import torch
import logging
import time
from tqdm import tqdm

logger = logging.getLogger("shadowfi")


def evaluate_model(model, device, test_loader, desc="Test"):
    """
    Evaluates the model on the test set and logs the accuracy and timing.

    Returns:
        float: accuracy
    """
    try:
        model.eval()
    except AttributeError:
        logger.warning(
            "⚠️ Loaded quantized model does not require .eval() or it's already applied."
        )

    correct = 0
    total = 0
    eval_bar = tqdm(test_loader, desc=f"{desc} Evaluation", leave=False, unit="batch")
    total_start = time.perf_counter()

    batch_times = []

    with torch.no_grad():
        for data, target in eval_bar:
            data, target = data.to(device), target.to(device)
            t0 = time.perf_counter()

            output = model(data)

            t1 = time.perf_counter()
            batch_time = t1 - t0
            batch_times.append(batch_time)

            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)

            eval_bar.set_postfix(
                accuracy=f"{100. * correct / total:.2f}%",
                batch_time=f"{batch_time:.4f}s"
            )

    total_end = time.perf_counter()
    total_time = total_end - total_start

    acc = 100.0 * correct / total

    forward_time = sum(batch_times)

    logger.info(f"⏱️ {desc} Total loop time: {total_time:.4f} seconds")
    logger.info(f"⏱️ {desc} Pure forward time: {forward_time:.4f} seconds")
    logger.info(f"⏱️ {desc} Avg batch forward time: {forward_time / len(batch_times):.6f} seconds")

    return acc
