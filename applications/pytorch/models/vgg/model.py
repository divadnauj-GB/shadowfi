import torch
import torch.nn as nn


class VGG11(nn.Module):
    def __init__(self, num_classes=10, in_chans=1, img_size=28, **kwargs):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(in_chans, 64, kernel_size=3, padding=1),  # 28x28
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 14x14

            nn.Conv2d(64, 128, kernel_size=3, padding=1),  # 14x14
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 7x7

            nn.Conv2d(128, 256, kernel_size=3, padding=1),  # 7x7
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),  # 7x7
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 3x3

            nn.Conv2d(256, 512, kernel_size=3, padding=1),  # 3x3
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 3x3
            nn.ReLU(inplace=True),

            nn.Conv2d(512, 512, kernel_size=3, padding=1),  # 3x3
            nn.ReLU(inplace=True),
        )

        self.classifier = nn.Sequential(
            nn.Linear(512 * 3 * 3, 512),
            nn.ReLU(inplace=True),

            nn.Linear(512, 256),
            nn.ReLU(inplace=True),

            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
