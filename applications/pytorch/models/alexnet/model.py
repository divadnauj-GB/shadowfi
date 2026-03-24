import torch
import torch.nn as nn


class AlexNet(nn.Module):
    def __init__(self, num_classes=10, in_chans=1, img_size=28, **kwargs):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(in_chans, 32, kernel_size=3, stride=1, padding=1),  # 28x28
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),  # 14x14

            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 14x14
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),  # 7x7

            nn.Conv2d(64, 128, kernel_size=3, padding=1),  # 7x7
            nn.ReLU(inplace=True),

            nn.Conv2d(128, 128, kernel_size=3, padding=1),  # 7x7
            nn.ReLU(inplace=True),

            nn.MaxPool2d(kernel_size=2),  # 3x3
        )

        self.classifier = nn.Sequential(
            nn.Linear(128 * 3 * 3, 256),
            nn.ReLU(inplace=True),

            nn.Linear(256, 128),
            nn.ReLU(inplace=True),

            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
