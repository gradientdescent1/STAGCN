import torch
import torch.nn as nn

from model import layers


class STGCNChebGraphConv(nn.Module):
    # STGCNChebGraphConv contains 'TGTND TGTND TNFF' structure
    # ChebGraphConv is the graph convolution from ChebyNet.
    # Using the Chebyshev polynomials of the first kind as a graph filter.

    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # G: Graph Convolution Layer (ChebGraphConv)
    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # N: Layer Normolization
    # D: Dropout

    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # G: Graph Convolution Layer (ChebGraphConv)
    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # N: Layer Normolization
    # D: Dropout

    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # N: Layer Normalization
    # F: Fully-Connected Layer
    # F: Fully-Connected Layer

    def __init__(self, args, blocks, n_vertex):
        super(STGCNChebGraphConv, self).__init__()
        modules = []
        n_his = args.n_his
        for l in range(len(blocks) - 3):
            # print(l)
            modules.append(layers.STConvBlock(args.Kt, args.Ks, n_vertex,
                                              blocks[l][-1], blocks[l+1], args.act_func, args.graph_conv_type, args.gso, args.enable_bias, args.droprate, n_his, l, args.framework))
            n_his -= 2
        self.st_blocks = nn.Sequential(*modules)
        Ko = args.n_his - (len(blocks) - 3) * 2 * (args.Kt - 1)
        self.Ko = Ko
        # self.Ko = 0
        if self.Ko > 1:
            self.output = layers.OutputBlock(
                Ko, blocks[-3][-1], blocks[-2], blocks[-1][0], n_vertex, args.act_func, args.enable_bias, args.droprate)
        elif self.Ko == 0:
            self.fc1 = nn.Linear(
                in_features=blocks[-3][-1], out_features=blocks[-2][0], bias=args.enable_bias)
            self.fc2 = nn.Linear(
                in_features=blocks[-2][0], out_features=blocks[-1][0], bias=args.enable_bias)
            self.relu = nn.ReLU()
            self.leaky_relu = nn.LeakyReLU()
            self.silu = nn.SiLU()
            self.dropout = nn.Dropout(p=args.droprate)

        # self.fc3 = nn.Linear(
        #     in_features=1, out_features=args.n_pred, bias=args.enable_bias)
        # self.n_vertex = n_vertex

    def forward(self, x):
        #print(f"initial shape = {x.shape}, self.Ko = {self.Ko}")
        x = self.st_blocks(x)
        #print(f"output of st blocks = {x.shape}")
        if self.Ko > 1:
            x = self.output(x)
            #print(f"K0 > 1 = {x.shape}")
        elif self.Ko == 0:
            #print(f"Ko == 0, = {x.shape}")
            x = self.fc1(x.permute(0, 2, 3, 1))
            #print(f"after fc1 in Ko = {x.shape}")
            x = self.relu(x)
            #print(f"after relu in Ko = {x.shape}")
            x = self.fc2(x).permute(0, 3, 1, 2)
            #print(f"after fc2 in Ko = {x.shape}")

        # print(f"Current pred shape = {x.shape}")

        # x = self.fc3(
        #     x.reshape(-1, 1, self.n_vertex).permute(0, 2, 1)).permute(0, 2, 1)

        # print(f"New pred shape = {x.shape}")

        return x


class STGCNGraphConv(nn.Module):
    # STGCNGraphConv contains 'TGTND TGTND TNFF' structure
    # GraphConv is the graph convolution from GCN.
    # GraphConv is not the first-order ChebConv, because the renormalization trick is adopted.
    # Be careful about over-smoothing.

    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # G: Graph Convolution Layer (GraphConv)
    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # N: Layer Normolization
    # D: Dropout

    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # G: Graph Convolution Layer (GraphConv)
    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # N: Layer Normolization
    # D: Dropout

    # T: Gated Temporal Convolution Layer (GLU or GTU)
    # N: Layer Normalization
    # F: Fully-Connected Layer
    # F: Fully-Connected Layer

    def __init__(self, args, blocks, n_vertex):
        super(STGCNGraphConv, self).__init__()
        modules = []
        n_his = args.n_his
        for l in range(len(blocks) - 3):
            modules.append(layers.STConvBlock(args.Kt, args.Ks, n_vertex,
                                              blocks[l][-1], blocks[l+1], args.act_func, args.graph_conv_type, args.gso, args.enable_bias, args.droprate, n_his, l, args.framework))
            n_his -= 2
        self.st_blocks = nn.Sequential(*modules)
        Ko = args.n_his - (len(blocks) - 3) * 2 * (args.Kt - 1)
        self.Ko = Ko
        if self.Ko > 1:
            self.output = layers.OutputBlock(
                Ko, blocks[-3][-1], blocks[-2], blocks[-1][0], n_vertex, args.act_func, args.enable_bias, args.droprate)
        elif self.Ko == 0:
            self.fc1 = nn.Linear(
                in_features=blocks[-3][-1], out_features=blocks[-2][0], bias=args.enable_bias)
            self.fc2 = nn.Linear(
                in_features=blocks[-2][0], out_features=blocks[-1][0], bias=args.enable_bias)
            self.relu = nn.ReLU()
            self.leaky_relu = nn.LeakyReLU()
            self.silu = nn.SiLU()
            self.do = nn.Dropout(p=args.droprate)

        # self.fc3 = nn.Linear(
        #     in_features=1, out_features=args.n_pred, bias=args.enable_bias)
        # self.n_vertex = n_vertex

    def forward(self, x):
        x = self.st_blocks(x)
        if self.Ko > 1:
            x = self.output(x)
        elif self.Ko == 0:
            x = self.fc1(x.permute(0, 2, 3, 1))
            x = self.relu(x)
            x = self.fc2(x).permute(0, 3, 1, 2)

        # print(f"Current pred shape = {x.shape}")

        # x = self.fc3(x.reshape(-1, 1, self.n_vertex))

        # print(f"New pred shape = {x.shape}")

        return x
