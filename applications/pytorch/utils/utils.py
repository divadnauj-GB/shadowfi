import torch
from pathlib import Path
import logging
from tqdm import (
    tqdm,
)

logger = logging.getLogger("shadowfi")


def get_device():
    """Determines and returns the appropriate device (MPS, CUDA, or CPU)."""
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        logger.info("Using MPS device (Apple Silicon GPU).")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info("Using CUDA device (NVIDIA GPU).")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU device.")
    return device


def ensure_dir(path: Path):
    """Ensures the parent directory of a given path exists."""
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path.parent}")


def ensure_file(path: Path):
    """Ensures the file exists."""
    if not path.exists():
        ensure_dir(path)
        path.touch()


def test(model, device, test_loader, desc="Test"):
    """
    Evaluates the model on the test set.

    Args:
        model (torch.nn.Module): The model to evaluate.
        device (torch.device): The device to run evaluation on.
        test_loader (torch.utils.data.DataLoader): DataLoader for the test set.
        desc (str): Description for the test phase (e.g., "FP32", "INT8").

    Returns:
        dict: A dictionary containing 'accuracy'.
    """
    model.eval()
    correct, total = 0, 0
    # Use tqdm for a progress bar during testing
    test_bar = tqdm(test_loader, desc=f"{desc} Evaluation", leave=False, unit="batch")
    with torch.no_grad():
        for data, target in test_bar:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)
            test_bar.set_postfix(
                accuracy=f"{100. * correct / total:.2f}%"
            )  # Update progress bar

    acc = 100.0 * correct / total
    logger.info(f"📊 {desc} Accuracy: {acc:.2f}% (Correct: {correct}/{total})")
    return {"accuracy": acc}


def train(model, device, train_loader, optimizer, criterion, epochs=6):
    """
    Trains the model.

    Args:
        model (torch.nn.Module): The model to train.
        device (torch.device): The device to run training on.
        train_loader (torch.utils.data.DataLoader): DataLoader for the training set.
        optimizer (torch.optim.Optimizer): The optimizer for training.
        criterion (torch.nn.Module): The loss function.
        epochs (int): Number of training epochs.
    """
    model.train()
    logger.info(f"Starting model training for {epochs} epochs...")
    for epoch in range(epochs):
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        # Use tqdm for a progress bar during training
        train_bar = tqdm(
            train_loader,
            desc=f"Epoch {epoch+1}/{epochs} Training",
            leave=False,
            unit="batch",
        )
        for batch_idx, (data, target) in enumerate(train_bar):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total_train += target.size(0)
            correct_train += (predicted == target).sum().item()

            # Update progress bar with current batch loss and accuracy
            train_bar.set_postfix(
                loss=running_loss / (batch_idx + 1),
                acc=f"{100.*correct_train/total_train:.2f}%",
            )

        avg_train_loss = running_loss / len(train_loader)
        train_accuracy = 100.0 * correct_train / total_train
        logger.info(
            f"✅ Epoch {epoch+1}/{epochs} complete | Train Loss: {avg_train_loss:.4f}, Train Accuracy: {train_accuracy:.2f}%"
        )
    logger.info("Training process finished.")
