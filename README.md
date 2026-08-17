# Multi-Object Dexterous Picking with Point Clouds

A framework for training a single dexterous manipulation policy to grasp diverse object types using multi-view point cloud observations.

## Overview

This project develops a unified policy for 5-fingered dexterous hands to grasp diverse objects (bowls, cups, kettles, bottles, plates, tools, etc.) using point cloud observations from exocentric and wrist-mounted cameras. The key insight is that normalizing visual inputs by object scale allows a single policy to generalize across object types without per-object fine-tuning.

**Core Assumption:** A single policy can learn effective grasping strategies for diverse objects if visual observations are normalized by bounding box scale—similar to how humans grasp objects of different sizes with similar hand configurations.

## Context

### Problem Statement
- **Hand:** 5-fingered dexterous manipulator (22 DoF: 5 fingers × 4 DoF + base translation/orientation)
- **Observations:** Multi-view point clouds (exo camera + wrist camera)
- **Goal:** Single policy for diverse object types—no per-object fine-tuning
- **Constraint:** Single object per episode (one grasp per trial), but object type varies

### Motivation
Inspired by the [DexArt](https://arxiv.org/abs/2404.02771) paper and related work on learning dense manipulation skills with point cloud priors. Unlike SAR or GraspXL approaches that require per-object fine-tuning, we aim for a truly generalizable policy through proper normalization.

## Key Design Decisions

### 1. Observation Representation

```
Observation = {
  bounding_box: [x, y, z, width, height, depth],        # 6D: object location & size
  object_scale: float,                                     # magnitude of size variation
  point_cloud: Nx3 points (world frame),                   # multi-view, unfiltered
  gripper_state: [joint_angles, gripper_width, velocity]   # current hand config
}
```

**Why this representation:**
- Bounding box anchors the object in space and provides scale cues
- Point cloud preserves geometry details (shape, surface features)
- Multi-view fusion reduces occlusion vs. single camera
- World-frame coordinates simplify hand-relative grasping

### 2. Scale Normalization Strategy

Objects vary 2-4× in linear dimension (e.g., small cup → large kettle). Normalization happens at the observation encoder input:

```python
# Pseudo-code for normalization
def normalize_for_policy(bbox, point_cloud, hand_state):
    # Normalize point cloud to object bounding box
    pc_centered = point_cloud - bbox[:3]  # center on object
    pc_scaled = pc_centered / bbox_scale  # normalize to unit scale
    
    # Normalize bounding box (record actual scale separately)
    bbox_normalized = [0, 0, 0, 1, 1, 1]  # unit bounding box
    
    # Hand state already in normalized scales (joint angles, gripper width)
    
    return {
        'pc': pc_scaled,
        'bbox': bbox_normalized,
        'scale': bbox_scale,
        'hand': hand_state
    }
```

**Benefits:**
- Encoder sees consistent input distribution regardless of object size
- Policy learns size-invariant grasping primitives
- Scale multiplier applied to action output for real-world execution

### 3. Training Paradigm

- **Single policy**: trained on 10-20 diverse object types simultaneously
- **No per-object fine-tuning**: unlike SAR, no adaptation phase per new object
- **Scale randomization**: during training, randomly scale object instances to expand coverage
- **Domain randomization**: mesh geometry, material properties, table friction

## Phased Approach

### Phase 1: Simple Grasping (Current)
**Setup:** One random object type per episode on empty table  
**Goal:** Establish baseline policy, validate scale normalization  
**Success metric:** ≥70% grasp success rate on 5-10 object types

**Deliverables:**
- Training pipeline with PPO + normalized point cloud encoder
- Evaluation on held-out test objects
- Baseline RL results and learning curves

### Phase 2: Cluttered Grasping (Next)
**Setup:** Target object among distractors; occlusion handling  
**Goal:** Improve robustness with realistic scene complexity  
**Success metric:** ≥60% grasp success in clutter

**Challenges to address:**
- Multi-view point cloud fusion with occlusions
- Bounding box detection in cluttered scenes
- Attention mechanisms to filter distractors

### Phase 3: Molmo Benchmark (Future)
**Setup:** Large-scale evaluation with Molmo objects  
**Goal:** Validate generalization to unseen object categories  
**Success metric:** Smooth transfer to new objects without retraining

## Open Questions

### 1. Primitives vs. Meshes for Training
| Aspect | Primitives | Meshes |
|--------|-----------|--------|
| **Simulation Speed** | 3-7 days | 1-2 weeks |
| **Geometry Realism** | ❌ Low | ✓ High |
| **Transfer Risk** | ⚠️ High (sim-to-real gap) | ✓ Lower |
| **Recommendation** | Phase 1 baseline | Phase 2+ |

**Decision:** Start with primitives for rapid iteration. Transition to meshes once Phase 1 shows promise.

### 2. Multi-View Strategy
**Options:**
- **Exo + wrist (current):** Two cameras, ~120° total coverage
- **Exo + wrist + side view:** Three cameras, more robust occlusion handling
- **Egocentric-only:** Wrist camera dominant, faster inference

**Decision:** Defer to Phase 1 results. Start with exo+wrist; add 3rd camera if needed.

### 3. Point Cloud Resolution
| Resolution | Memory | Detail | Speed |
|------------|--------|--------|-------|
| **128 points** | ✓ Low | ❌ Coarse | ✓ Fast |
| **512 points** | ✓ Medium | ✓ Good | ✓ Reasonable |
| **1024 points** | ⚠️ High | ✓✓ Detailed | ❌ Slow |

**Preliminary choice:** 512 points; balance detail vs. compute. Ablate in Phase 1.

### 4. Architecture: Encoder to Action

```python
# Simplified architecture
class DexterousPickingPolicy(nn.Module):
    def __init__(self):
        self.point_encoder = PointNet(input_dim=3, output_dim=256)
        self.bbox_encoder = nn.Linear(6, 64)
        self.scale_encoder = nn.Linear(1, 32)
        self.hand_state_encoder = nn.Linear(28, 64)  # 28 for hand state
        
        self.fusion = nn.Linear(256 + 64 + 32 + 64, 256)
        self.policy_head = nn.Linear(256, 22)  # 22 DoF action
        self.value_head = nn.Linear(256, 1)
    
    def forward(self, obs):
        # obs = {pc, bbox, scale, hand_state}
        pc_feat = self.point_encoder(obs['pc'])          # (B, 256)
        bbox_feat = self.bbox_encoder(obs['bbox'])       # (B, 64)
        scale_feat = self.scale_encoder(obs['scale'])    # (B, 32)
        hand_feat = self.hand_state_encoder(obs['hand']) # (B, 64)
        
        fused = self.fusion(
            torch.cat([pc_feat, bbox_feat, scale_feat, hand_feat], dim=-1)
        )
        
        action = self.policy_head(fused)        # (B, 22)
        value = self.value_head(fused)          # (B, 1)
        
        return action, value
```

**Rationale:**
- **PointNet encoder** captures geometric features (standard for point clouds)
- **Separate bbox/scale encoding** ensures size cues are explicit
- **Fusion layer** combines multi-modal inputs
- **PPO training** on action space with clipped rewards

## Preliminary Architecture

### High-Level Pipeline

```
[Exo Camera + Wrist Camera]
            ↓
   [Point Cloud Fusion & Filtering]
            ↓
   [Bounding Box Detection (DINO / SAM)]
            ↓
   [Normalization (scale-invariant)]
            ↓
    [Policy Network (PointNet + Dense)]
            ↓
    [Action Output: 22-DoF motor commands]
            ↓
   [Dexterous Hand Execution]
```

### Training Loop

1. **Rollout:** Collect trajectories from 5-20 random object types
2. **Normalize:** Apply scale normalization to observations
3. **PPO Update:** Compute policy and value losses
4. **Domain Randomize:** Vary object scale, material, appearance
5. **Evaluate:** Test on held-out object instances

### Reward Function (Phase 1)

```python
def grasp_reward(gripper_force, object_lifted, episode_time):
    reward = 0
    
    # Contact reward: encourage finger contact
    if gripper_force > threshold:
        reward += 1.0
    
    # Lift reward: success is lifting object off table
    if object_lifted:
        reward += 5.0
    
    # Time penalty: favor faster grasps
    time_penalty = episode_time * 0.01
    
    return reward - time_penalty
```

## Next Steps

### Immediate (Week 1-2)
- [ ] Decide: Primitives vs. meshes for Phase 1
- [ ] Define point cloud resolution and filtering
- [ ] Implement Phase 1 baseline (10 primitive object types)
- [ ] Set up training infrastructure (PPO, normalization pipeline)

### Short-term (Week 3-6)
- [ ] Train policy on 10-20 objects; benchmark learning curves
- [ ] Ablate design choices (resolution, architecture, normalization)
- [ ] Evaluate sim-to-real transfer on 2-3 real objects

### Medium-term (Week 7-12)
- [ ] Phase 2: Cluttered grasping with bounding box detection
- [ ] Multi-view fusion improvements if needed
- [ ] Add grasp quality metrics (force, stability)

### Long-term (Month 4+)
- [ ] Phase 3: Molmo benchmark evaluation
- [ ] Unseen object generalization study
- [ ] Compare to per-object fine-tuning baselines (SAR, GraspXL)

## Project Structure

- `config/` — Configuration files and system setup
- `docs/` — Architecture decisions, assumptions, research findings
- `src/` — Python source code (encoders, policies, training loops)
- `scripts/` — Utility scripts for data processing, evaluation
- `assets/` — Asset references and object definitions
- `experiments/` — Experiment configurations and results

## References

- **DexArt:** [Dexterous Manipulation with Object-Centric Point Clouds](https://arxiv.org/abs/2404.02771)
- **PointNet:** [PointNet: Deep Learning on Point Sets for 3D Classification and Segmentation](https://arxiv.org/abs/1612.00593)
- **PPO:** [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)
- **SAR / GraspXL:** Per-object adaptation baselines for comparison

## Quick Start

1. **Set mjlab path:**
   ```bash
   export MJLAB_PATH="/path/to/simtoolreal_mjlab/mjlab"
   ```

2. **Install:**
   ```bash
   uv venv && source venv/bin/activate
   uv pip install -e .
   ```

3. **Check config:**
   ```bash
   python -c "from multi_object_porting.config import cfg; print(cfg)"
   ```

See `config/SYSTEM_SETUP.md` for system-specific instructions and `docs/DECISIONS.md` for architecture rationale.
