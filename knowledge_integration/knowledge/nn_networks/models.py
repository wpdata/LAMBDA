import math
from torch import nn
from torch.nn.utils.parametrizations import spectral_norm


def initialize_weights(tensor):
    return tensor.uniform_() * math.sqrt(0.25 / (tensor.shape[0] + tensor.shape[1]))


class _RRAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_1 = nn.Linear(784, 200)
        self.linear_2 = nn.Linear(200, 784)
        self.encoder = self.linear_1
        self.decoder = self.linear_2

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)

        return x

    def clamp(self):
        pass


class _NNAutoencoder(_RRAutoencoder):
    def __init__(self):
        super().__init__()
        self.linear_1.bias.data.zero_()
        self.linear_2.bias.data.zero_()
        self.linear_1.weight = nn.Parameter(
            initialize_weights(self.linear_1.weight.data)
        )
        self.linear_2.weight = nn.Parameter(
            initialize_weights(self.linear_2.weight.data)
        )

    def clamp(self):
        self.linear_1.weight.data.clamp_(min=0)
        self.linear_2.weight.data.clamp_(min=0)
        self.linear_1.bias.data.clamp_(min=0)
        self.linear_2.bias.data.clamp_(min=0)


class _PNAutoencoder(_NNAutoencoder):
    def clamp(self):
        self.linear_1.weight.data.clamp_(min=1e-3)
        self.linear_2.weight.data.clamp_(min=1e-3)
        self.linear_1.bias.data.clamp_(min=0)
        self.linear_2.bias.data.clamp_(min=0)


class _NRAutoencoder(_NNAutoencoder):
    def clamp(self):
        self.linear_1.weight.data.clamp_(min=0)
        self.linear_2.weight.data.clamp_(min=0)


class SigmoidNNAutoencoder(_NNAutoencoder):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(self.linear_1, nn.Sigmoid())
        self.decoder = nn.Sequential(self.linear_2, nn.Sigmoid())


class TanhNNAutoencoder(_NNAutoencoder):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(self.linear_1, nn.Tanh())
        self.decoder = nn.Sequential(self.linear_2, nn.Tanh())


class TanhPNAutoencoder(_PNAutoencoder):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(self.linear_1, nn.Tanh())
        self.decoder = nn.Sequential(self.linear_2, nn.Tanh())


class ReLUNNAutoencoder(_NNAutoencoder):
    def __init__(self):
        super().__init__()
        self.linear_1 = spectral_norm(self.linear_1)
        self.linear_2 = spectral_norm(self.linear_2)
        self.encoder = nn.Sequential(self.linear_1, nn.ReLU())
        self.decoder = nn.Sequential(self.linear_2, nn.ReLU())

    def clamp(self):
        self.linear_1.parametrizations.weight.original.data.clamp_(min=0)
        self.linear_2.parametrizations.weight.original.data.clamp_(min=0)
        self.linear_1.bias.data.clamp_(min=0)
        self.linear_2.bias.data.clamp_(min=0)


class ReLUPNAutoencoder(_PNAutoencoder):
    def __init__(self):
        super().__init__()
        self.linear_1 = spectral_norm(self.linear_1)
        self.linear_2 = spectral_norm(self.linear_2)
        self.encoder = nn.Sequential(self.linear_1, nn.ReLU())
        self.decoder = nn.Sequential(self.linear_2, nn.ReLU())

    def clamp(self):
        self.linear_1.parametrizations.weight.original.data.clamp_(min=1e-3)
        self.linear_2.parametrizations.weight.original.data.clamp_(min=1e-3)
        self.linear_1.bias.data.clamp_(min=0)
        self.linear_2.bias.data.clamp_(min=0)


class TanhSwishNNAutoencoder(_NNAutoencoder):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(self.linear_1, nn.Tanh())
        self.decoder = nn.Sequential(self.linear_2, nn.SiLU())


class ReLUSigmoidNRAutoencoder(_NRAutoencoder):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(self.linear_1, nn.ReLU())
        self.decoder = nn.Sequential(self.linear_2, nn.Sigmoid())


class ReLUSigmoidRRAutoencoder(_RRAutoencoder):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(self.linear_1, nn.ReLU())
        self.decoder = nn.Sequential(self.linear_2, nn.Sigmoid())
