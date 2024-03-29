import torch
import torch.nn as nn
from layers.units import Conv2d


class Stem(nn.Module):
    def __init__(self, in_channels):
        super(Stem, self).__init__()
        self.conv = Conv2d(in_channels, 32, 4, stride=2, padding=0, bias=False)

    def forward(self, x):
        x = self.conv(x)
        return x


class InceptionResNetA(nn.Module):
    def __init__(self, in_channels, scale=1.0):
        super(InceptionResNetA, self).__init__()
        self.scale = scale
        self.branch0 = Conv2d(in_channels, in_channels, 1, stride=1, padding=0, bias=False)
        self.branch1 = nn.Sequential(
            Conv2d(in_channels, in_channels, 1, stride=1, padding=0, bias=False),
            Conv2d(in_channels, in_channels, 3, stride=1, padding=0, bias=False)
        )
        self.branch2 = nn.Sequential(
            Conv2d(in_channels, in_channels, 1, stride=1, padding=0, bias=False),
            Conv2d(in_channels, int(1.5*in_channels), 3, stride=1, padding=0, bias=False),
            Conv2d(int(1.5*in_channels), int(2*in_channels), 3, stride=1, padding=0, bias=False)
        )
        self.linear = Conv2d(
            in_channels+int(1.5*in_channels)+int(2*in_channels),
            in_channels, 1, stride=1, padding=0, bias=False)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        b0 = self.branch0(x)
        b1 = self.branch1(x)
        b2 = self.branch2(x)
        concat = torch.cat((b0, b1, b2), dim=1)
        linear = self.linear(concat)
        result = self.relu(x + linear)
        return result


class ReductionA(nn.Module):
    def __init__(self, in_channels, scale=1.0):
        super(ReductionA, self).__init__()
        self.scale = scale
        self.branch0 = nn.MaxPool2d(3, stride=2, padding=0)
        self.branch1 = nn.Conv2d(in_channels, int(1.5*in_channels), 3, stride=2, padding='valid', bias=False)
        self.branch2 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False),
            nn.Conv2d(in_channels, in_channels, 3, stride=1, bias=False),
            nn.Conv2d(in_channels, int(1.5*in_channels), 3, stride=2, bias=False)
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        b0 = self.branch0(x)
        b1 = self.branch1(x)
        b2 = self.branch2(x)
        b012 = torch.cat((b0, b1, b2), dim=1)
        relued = self.relu(b012)
        return relued


class InceptionResNetB(nn.Module):
    def __init__(self, in_channels, scale=1.0):
        super(InceptionResNetB, self).__init__()
        self.scale = scale
        self.branch0 = nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False)
        self.branch1 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False),
            nn.Conv2d(in_channels, int(1.25*in_channels), (1, 7), stride=1, padding='same', bias=False),
            nn.Conv2d(int(1.25*in_channels), int(1.50*in_channels), (7, 1), stride=1, padding='same', bias=False)
        )
        self.linear = nn.Conv2d(int(1.50*in_channels)+in_channels, in_channels, 1, stride=1, padding='same', bias=False)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        b0 = self.branch0(x)
        b1 = self.branch1(x)
        concat = torch.cat((b0, b1), dim=1)
        linear = self.linear(concat)
        relu = self.relu(x + linear)
        return relu


class ReductionB(nn.Module):
    def __init__(self, in_channels, scale=1):
        super(ReductionB, self).__init__()
        scale = 1
        self.maxpool = nn.MaxPool2d(3, stride=2, padding=0)
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False),
            nn.Conv2d(in_channels, int(1.5 * in_channels), 3, stride=2, padding=0, bias=False)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False),
            nn.Conv2d(in_channels, int(1.125 * in_channels), 3, stride=2, padding=0, bias=False)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False),
            nn.Conv2d(in_channels, int(1.125*in_channels), (3, 1), stride=1, padding='same', bias=False),
            nn.Conv2d(int(1.125*in_channels), int(1.25*in_channels), (3, 1), stride=2, padding=0, bias=False)
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        maxpool = self.maxpool(x)
        conv1 = self.conv1(x)
        conv2 = self.conv2(x)
        conv3 = self.conv3(x)
        concat = torch.cat((maxpool, conv1, conv2, conv3), dim=1)
        relu = self.relu(concat)
        return relu


class InceptionResNetC(nn.Module):
    def __init__(self, in_channels, scale=1.0):
        super(InceptionResNetC, self).__init__()
        self.scale = scale
        self.conv1 = nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False)
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 1, stride=1, padding='same', bias=False),
            nn.Conv2d(in_channels, int(1.16*in_channels), (1,3), stride=1, padding='same', bias=False),
            nn.Conv2d(int(1.16 * in_channels), int(1.33 * in_channels), (3, 1), stride=1, padding='same', bias=False)
        )
        self.linear = nn.Conv2d(in_channels + int(1.33 * in_channels), 1, stride=1, padding='same', bias=False)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        conv1 = self.conv1(x)
        conv2 = self.conv2(x)
        concat = torch.cat((conv1, conv2), dim=1)
        linear = self.linear(concat)
        relu = self.relu(x + linear)
        return relu


class Chemception(nn.Module):
    def __init__(self, in_channels, n_a, n_b, n_c):
        super(Chemception, self).__init__()
        # Input: Bx80x80x1
        blocks = [Stem(in_channels)]

        # Input: Bx40x40x1
        blocks.extend([InceptionResNetA(in_channels) for i in range(n_a)])

        # Input: Bx40x40x64
        blocks.append(ReductionA(in_channels))

        # Input: Bx19x19x256
        blocks.append([InceptionResNetB(in_channels) for i in range(n_b)])

        # Input: Bx19x19x640
        blocks.append(ReductionB(in_channels))

        # Input: Bx9x9x3120
        blocks.append([InceptionResNetC(in_channels)] for i in range(n_c))
        # Output: Bx9x9x7270

        self.network = nn.Sequential(*blocks)

    def forward(self, x):
        x = self.network(x)
        return x
