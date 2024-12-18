from models import (
    SigmoidNNAutoencoder,
    TanhNNAutoencoder,
    TanhPNAutoencoder,
    ReLUNNAutoencoder,
    ReLUPNAutoencoder,
    TanhSwishNNAutoencoder,
    ReLUSigmoidNRAutoencoder,
    ReLUSigmoidRRAutoencoder,
)
from tqdm import tqdm


def get_network(name):
    match name:
        case "nn_sigmoid":
            return SigmoidNNAutoencoder()
        case "nn_tanh":
            return TanhNNAutoencoder()
        case "pn_tanh":
            return TanhPNAutoencoder()
        case "nn_relu":
            return ReLUNNAutoencoder()
        case "pn_relu":
            return ReLUPNAutoencoder()
        case "nn_tanh_swish":
            return TanhSwishNNAutoencoder()
        case "nr_relu_sigmoid":
            return ReLUSigmoidNRAutoencoder()
        case "rr_relu_sigmoid":
            return ReLUSigmoidRRAutoencoder()
        case _:
            raise NotImplementedError(
                f"Autoencoder of name '{name}' currently is not supported"
            )


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def epoch(loader, model, device, criterion, opt=None):
    losses = AverageMeter()

    if opt is None:
        model.eval()
    else:
        model.train()
    for inputs, _ in tqdm(loader, leave=False):
        inputs = inputs.view(-1, 28 * 28).to(device)
        outputs = model(inputs)
        loss = criterion(outputs, inputs)
        if opt:
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            model.clamp()

        losses.update(loss.item(), inputs.size(0))

    return losses.avg
