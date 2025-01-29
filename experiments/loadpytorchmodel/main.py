import torch

from models import UNet

model = torch.load("D:\\Mosamatic\\PyTorchModelFiles\\model_full_100000.pth")
model.to('cpu')
model.eval()