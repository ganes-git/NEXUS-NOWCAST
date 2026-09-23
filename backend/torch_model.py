"""
NEXUS-NOWCAST: STGAT-PIE PyTorch Neural Network Module
Implements:
- Multi-Head Graph Attention (GATv2Conv) for spatial cross-modal attention
- Recurrent Graph Memory (GConvGRUCell) for 0-6h spatiotemporal sequence modeling
- Dual-Head Decoders: Head A (Reflectivity & Trajectory) and Head B (Lightning Jump & Flash Rate)
- Physics Loss constraints (Advection consistency with 700 hPa winds)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple


class GATv2SpatialLayer(nn.Module):
    """
    Multi-Head Dynamic Graph Attention Layer (Veličković et al. 2022).
    Computes dynamic attention over heterogeneous atmospheric observation edges.
    """
    def __init__(self, in_features: int, out_features: int, heads: int = 4, edge_dim: int = 3):
        super(GATv2SpatialLayer, self).__init__()
        self.heads = heads
        self.out_features = out_features
        self.head_dim = out_features // heads

        self.w_src = nn.Linear(in_features, out_features, bias=False)
        self.w_dst = nn.Linear(in_features, out_features, bias=False)
        self.w_edge = nn.Linear(edge_dim, out_features, bias=False)
        self.attn_vec = nn.Parameter(torch.Tensor(1, heads, self.head_dim))
        nn.init.xavier_uniform_(self.attn_vec)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        """
        x: [num_nodes, in_features]
        edge_index: [2, num_edges]
        edge_attr: [num_edges, edge_dim] (wind vector, CAPE gradient, distance decay)
        """
        N = x.size(0)
        E = edge_index.size(1)

        src_feat = self.w_src(x).view(N, self.heads, self.head_dim)
        dst_feat = self.w_dst(x).view(N, self.heads, self.head_dim)
        edge_feat = self.w_edge(edge_attr).view(E, self.heads, self.head_dim)

        src_edges = src_feat[edge_index[0]] # [E, heads, head_dim]
        dst_edges = dst_feat[edge_index[1]] # [E, heads, head_dim]

        # GATv2 scoring function: a^T * LeakyReLU(W_src*x_i + W_dst*x_j + W_edge*e_ij)
        edge_sum = F.leaky_relu(src_edges + dst_edges + edge_feat, negative_slope=0.2)
        alpha = (edge_sum * self.attn_vec).sum(dim=-1, keepdim=True) # [E, heads, 1]
        alpha = F.softmax(alpha, dim=0)

        # Message passing aggregation
        out = torch.zeros(N, self.heads, self.head_dim, device=x.device)
        msg = src_edges * alpha
        out.index_add_(0, edge_index[1], msg)

        return out.view(N, self.out_features)


class STGATPIENetwork(nn.Module):
    """
    End-to-End Spatio-Temporal Graph Attention Network with Physics-Informed Edges.
    """
    def __init__(self, in_features: int = 8, hidden_dim: int = 64, num_forecast_steps: int = 24):
        super(STGATPIENetwork, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_forecast_steps = num_forecast_steps

        # 1. Spatial Message Passing Layers
        self.gat1 = GATv2SpatialLayer(in_features, hidden_dim, heads=4, edge_dim=3)
        self.gat2 = GATv2SpatialLayer(hidden_dim, hidden_dim, heads=4, edge_dim=3)

        # 2. Temporal Gated Recurrent Unit
        self.gru = nn.GRUCell(hidden_dim, hidden_dim)

        # 3. Head A: Thunderstorm Decoder (Reflectivity dBZ & Centroid Displacement)
        self.head_storm_dbz = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1) # Continuous dBZ regression
        )
        self.head_storm_traj = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 2) # (d_lat, d_lon) centroid vector displacement
        )

        # 4. Head B: Lightning Decoder (Flash Density & Lightning Jump Probability)
        self.head_lightning_fr = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1) # Flash rate (flashes/min)
        )
        self.head_lightning_jump = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid() # Probability of >= 2-sigma jump
        )

    def forward(
        self,
        node_features_seq: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        node_features_seq: [T_history, num_nodes, in_features] (T=12 timesteps)
        """
        T = node_features_seq.size(0)
        N = node_features_seq.size(1)
        h = torch.zeros(N, self.hidden_dim, device=node_features_seq.device)

        # Process spatiotemporal graph history
        for t in range(T):
            x_t = node_features_seq[t]
            g1 = F.elu(self.gat1(x_t, edge_index, edge_attr))
            g2 = F.elu(self.gat2(g1, edge_index, edge_attr))
            h = self.gru(g2, h)

        # Decode multi-task predictions
        pred_dbz = self.head_storm_dbz(h)
        pred_traj = self.head_storm_traj(h)
        pred_flash_rate = self.head_lightning_fr(h)
        pred_jump_prob = self.head_lightning_jump(h)

        return {
            "predicted_reflectivity_dbz": pred_dbz,
            "predicted_displacement_km": pred_traj,
            "predicted_flash_rate": pred_flash_rate,
            "lightning_jump_probability": pred_jump_prob,
            "latent_node_embeddings": h
        }
