import torch
import torch.nn as nn


class LeNet(nn.Module):
    def __init__(self, num_classes=10, in_chans=1, img_size=28, **kwargs):
        super(LeNet, self).__init__()

        self.quant = torch.quantization.QuantStub()
        self.dequant = torch.quantization.DeQuantStub()

        self.conv1 = nn.Conv2d(1, 6, kernel_size=5)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.AvgPool2d(kernel_size=2)

        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.AvgPool2d(kernel_size=2)

        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(120, 84)
        self.relu4 = nn.ReLU()
        self.fc3 = nn.Linear(84, num_classes)

    def forward(self, x):
        x = self.quant(x)

        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.reshape(x.size(0), -1)
        x = self.relu3(self.fc1(x))
        x = self.relu4(self.fc2(x))
        x = self.fc3(x)

        x = self.dequant(x)
        return x

    def fuse_model(self):
        torch.quantization.fuse_modules(
            self,
            [
                ["conv1", "relu1"],
                ["conv2", "relu2"],
                ["fc1", "relu3"],
                ["fc2", "relu4"],
            ],
            inplace=True,
        )
