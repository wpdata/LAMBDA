import argparse
from pathlib import Path

import torch
from torch import nn
from torch import optim
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision import datasets
from utils import get_network, epoch

torch.manual_seed(0)


def train_nn_network(args):

    p = Path(__file__)
    weights_path = f"{p.parent}/weights"
    Path(weights_path).mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = get_network(args.net)
    model.to(device)
    mnist_train = datasets.MNIST(
        ".", train=True, download=True, transform=transforms.ToTensor()
    )
    mnist_test = datasets.MNIST(
        ".", train=False, download=True, transform=transforms.ToTensor()
    )
    train_loader = DataLoader(
        mnist_train, batch_size=args.b, shuffle=True, num_workers=4, pin_memory=True
    )
    test_loader = DataLoader(
        mnist_test, batch_size=args.b, shuffle=False, num_workers=4, pin_memory=True
    )
    opt = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wd)
    criterion = nn.MSELoss()

    best_loss = None

    for i in range(1, args.epochs + 1):
        train_loss = epoch(train_loader, model, device, criterion, opt)
        test_loss = epoch(test_loader, model, device, criterion)
        if best_loss is None or best_loss > test_loss:
            best_loss = test_loss
            torch.save(model.state_dict(), f"{weights_path}/{args.net}.pth")

        print(f"Epoch: {i} | Train Loss: {train_loss:.4f} | Test Loss: {test_loss:.4f}")


if __name__ == "__main__":
    train_nn_network()
