import matplotlib.pyplot as plt
import numpy as np
import os
import re


def plot_loss_curves(file):
    all_text = None
    with open(file, "r", encoding="cp437", errors='ignore') as f:
        all_text = f.read()

    regex_train = r"Train loss: (\d*.\d*)"
    regex_val = r"Val loss: (\d*.\d*)"

    losses_train = re.findall(regex_train, all_text)
    losses_val = re.findall(regex_val, all_text)

    plt.figure(figsize=(8, 8))
    plt.plot(range(len(losses_train)), losses_train, label="Train Loss")
    plt.plot(range(len(losses_val)), losses_val, label="Val Loss")
    plt.legend(loc="upper right")
    plt.title(f"Loss vs Epochs for {file.rstrip('.txt')}")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    framework = file.rstrip('.txt').lstrip('./logs/')
    plt.savefig(f"./images/{framework}.png")
    plt.show()


if __name__ == "__main__":
    files = os.listdir("./logs")
    for file in files:
        print(file)
        plot_loss_curves(os.path.join("./logs", file))
