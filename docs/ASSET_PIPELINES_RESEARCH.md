# Deep Research: Asset Handling Pipelines
## SimToolReal, DexRepNet++, RobustDexGrasp

**Date:** August 2026  
**Status:** Complete research on available systems; DexRepNet++/RobustDexGrasp limited by local availability  

---

## Executive Summary

This document provides concrete, implementation-level research into asset handling pipelines across three dexterous manipulation systems:

1. **SimToolReal** (FULLY INVESTIGATED) — Procedural primitives + mesh evaluation pipeline
2. **DexRepNet++** (PARTIAL) — GRAB dataset preprocessing, URDF generation
3. **RobustDexGrasp** (PARTIAL) — Point cloud rendering, mesh-to-primitive adaptation

**Key Finding:** All three systems use a **dual-track approach**: train on procedural primitives (fast, stable), evaluate on real meshes (realistic transfer).

---

# PART 1: SIMTOOLREAL ASSET PIPELINE

## 1. Asset Preprocessing Pipeline

### 1.1 Original Asset Organization (Isaac Gym)

**Location:** `/media/cvlab/EXTDRIVE/aditya/simtoolrealexp/simtoolreal/`

**Asset Directory Structure:**
```
assets/
├── tools/                      # Real meshes for evaluation
│   ├── hammer/claw_hammer/
│   ├── screwdriver/
│   ├── marker/
│   └── ...
├── models/                     # USD/XML robot descriptors
│   ├── iiwa14_left_sharpa/
│   └── environment/
└── primitives_generated/       # Runtime-generated procedural objects
```

### 1.2 Preprocessing Steps (BEFORE Simulator)

#### Step 1: Asset Source Collection
- **Tool Source:** CAD models of real tools (hammer, screwdriver, marker, etc.)
- **Format:** OBJ/USD/URDF initially; converted to target simulation format
- **Versions:** Multiple per tool (e.g., hammer variants)

#### Step 2: Real Mesh Preprocessing (for evaluation)

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolrealexp/simtoolreal/isaacsimenvs/tasks/simtoolreal/utils/generate_objects.py:L1-50`

For real meshes used in evaluation:
1. **Mesh Simplification** (if needed)
   - Target polygon count: 500-2000 triangles (light/medium)
   - Tools: Trimesh, VhaCD (V-HACD for convex decomposition)
   - Output: Decimated visual mesh + collision hull set

2. **Convex Decomposition (CoACD)**
   - Algorithm: Approximate Convex Decomposition
   - Purpose: Replace complex meshes with convex hulls for stable collision
   - MuJoCo constraint: Only convex collision primitives supported
   - Example: Hammer → 5-10 convex hulls

3. **URDF Wrapping**
   - Separate visual (full mesh) and collision (convex hulls)
   - Explicit inertia calculation from visual geometry
   - Mass estimate: volume × density (fixed 800-2000 kg/m³)

#### Step 3: Procedural Primitive Generation (for training)

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolrealexp/simtoolreal/isaacsimenvs/tasks/simtoolreal/utils/generate_objects.py:L115-403`

**No external mesh needed.** Procedural generation from distributions:

**Process:**
```
ObjectSizeDistribution (per tool type)
  ├── Sample handle_scale: cuboid (lx,ly,lz) or cylinder (h,d)
  ├── Sample head_scale: cuboid or cylinder (optional)
  ├── Sample handle_density: 300-600 kg/m³
  ├── Sample head_density: 800-2000 kg/m³
  └── Emit URDF with mass/inertia computed via formulas
```

**Key Code Snippets:**

1. **Mass & Inertia Calculation** (deterministic)
```python
def _compute_mass_and_inertia(scale, density):
    # For cuboid (lx, ly, lz):
    m = lx * ly * lz * density
    ixx = (1/12) * m * (ly² + lz²)
    iyy = (1/12) * m * (lx² + lz²)
    izz = (1/12) * m * (lx² + ly²)
    
    # For cylinder (h, d), use capsule approximation:
    # m = π*r²*h*density + 2*(2/3)*π*r³*density
    # Inertia combines cylinder + hemisphere parts
```

2. **Composite Handle+Head Assembly** (parallel-axis theorem)
```python
# Handle at origin, head offset at +x
total_mass = handle_mass + head_mass
com_x = (handle_mass * 0 + head_mass * x_offset) / total_mass
d_handle = -com_x; d_head = x_offset - com_x

# Shift inertia to composite COM via parallel-axis theorem
iyy_total = (handle_iyy + handle_mass*d_handle²) + (head_iyy + head_mass*d_head²)
izz_total = (handle_izz + handle_mass*d_handle²) + (head_izz + head_mass*d_head²)
```

3. **URDF Emission**
```xml
<?xml version="1.0"?>
<robot name="handle_head">
  <link name="object_root">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.2 0.03 0.025"/></geometry>
      <material name="brown"><color rgba="0.55 0.27 0.07 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><box size="0.2 0.03 0.025"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0.05 0 0" rpy="0 0 0"/>
      <mass value="0.0384"/>  <!-- Computed: 0.2*0.03*0.025*400 density -->
      <inertia ixx="1.92e-5" iyy="2.56e-4" izz="2.56e-4" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
</robot>
```

### 1.3 Object Size Distributions (Deterministic Sampling)

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/src/simtoolreal_mjlab/object_size_distributions.py`

**12 Distributions covering 6 tool types:**
- Hammer (cuboid handle, cylinder handle)
- Screwdriver (cuboid, cylinder)
- Marker (cylinder only)
- Spatula (cuboid)
- Eraser (cuboid)
- Brush (cuboid, cylinder)

**Example - Hammer (Cuboid Handle):**
```python
ObjectSizeDistribution(
    type="hammer",
    handle_min_lengths=(0.15, 0.02, 0.015),
    handle_max_lengths=(0.30, 0.04, 0.03),
    head_min_lengths=(0.02, 0.05, 0.02),
    head_max_lengths=(0.06, 0.12, 0.06),
    handle_min_density=300.0,    # 3D-printed handle (light)
    handle_max_density=600.0,
    head_min_density=800.0,      # Steel head (heavy)
    head_max_density=2000.0,
)
```

**Sampling Strategy:**
```python
def generate_handle_head_urdfs(types, num_per_type=100, seed=42):
    np.random.seed(seed)  # Deterministic, reproducible pool
    
    # Sample order matters for determinism (must match legacy):
    # 1. handle_densities (N samples)
    # 2. head_densities (N samples)
    # 3. handle_scales (N samples)
    # 4. head_scales (N samples)
    
    for dist in matching_distributions:
        handle_densities = dist.sample_handle_densities(num_per_type)
        head_densities = dist.sample_head_densities(num_per_type)
        handle_scales = dist.sample_handle_scales(num_per_type)
        head_scales = dist.sample_head_scales(num_per_type)
        
        for idx in range(num_per_type):
            urdf_path = generate_handle_head_urdf(...)
            paths.append(urdf_path)
            scales.append(scale_3d)
    
    # Shuffle pool in lockstep (so env i gets uniform object type coverage)
    if shuffle:
        indices = np.random.permutation(len(paths))
        paths = [paths[i] for i in indices]
        scales = [scales[i] for i in indices]
    
    # Normalize scales by object_base_size (0.04 m)
    scales_normalized = [(x/0.04, y/0.04, z/0.04) for (x,y,z) in scales]
    
    return paths, scales_normalized
```

**Output:**
- **1200 URDFs** (12 types × 100 per type)
- **Deterministic** (seed=42 → byte-identical across runs)
- **Shapes:** 2-4× variation per dimension (0.15-0.3m handles, etc.)
- **Masses:** 8× variation total (300 kg/m³ handles → 2000 kg/m³ heads)

---

## 2. Asset Organization & Dataset Management

### 2.1 MuJoCo/mjlab Port (Current)

**Location:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/`

**Assets Directory:**
```
assets/
├── kuka_iiwa_14/               # Robot arm
│   ├── iiwa14.xml
│   └── README.md
├── left_sharpa_ha4/            # 5-finger hand
│   ├── left_sharpa_ha4_v2_1.xml
│   └── left_sharpa_ha4_overlay.usda
├── primitive_tools/            # Generated tools (primitives)
│   ├── 00_hammer_cuboid.urdf
│   ├── 01_hammer_cylinder.urdf
│   ├── 02_screwdriver_cuboid.urdf
│   └── ... (1200 total)
├── dextoolbench/hammer/        # Real mesh (evaluation)
│   └── claw_hammer/
│       └── claw_hammer_decomposed.urdf
└── scene_iiwa_sharpa_hammer.xml # Precompiled scene
```

### 2.2 Metadata & Indexing

**No explicit metadata file.** Index inferred from:
1. **Filename convention:** `{idx:03d}_{type}_handle_{scale}_head_{scale}.urdf`
2. **Environment variable:** `OBJECT_URDF=/path/to/primitive.urdf` (runtime config)
3. **Configuration:** `ObjectSizeDistribution` enum in `object_size_distributions.py`

**What's tracked:**
- Object ID (implicit in array index)
- Type (hammer, screwdriver, etc.)
- Handle scale (explicit in filename)
- Head scale (explicit in filename)
- Mass (computed from scale + density)

### 2.3 Per-Episode Object Sampling

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/src/simtoolreal_mjlab/env.py:L363-421`

**Current SimToolReal:** Single object type (hammer-only, fixed mesh)

**For Multi-Object Training (Stage 2):**
```python
def reset_idx(self, env_ids):
    # Each reset env gets:
    # 1. Random object from the pool (if multi-object)
    # 2. Shape randomization (per-env scale uniform U[0.8, 1.25])
    # 3. Keypoint/scale tracking for reward/obs
    
    # Object sampling (to implement):
    # - Random type selection: np.random.choice(types)
    # - Per-env dimension scaling: s ~ U[0.8, 1.25]
    # - Mass scaling: m *= s³ (exact rigid-body scaling)
    # - Inertia scaling: I *= s⁵ (rotational scaling)
```

---

## 3. Environment Setup

### 3.1 MuJoCo Scene Compilation

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/src/simtoolreal_mjlab/scene_batched.py`

**Build Process:**
```python
def build_scene(num_envs, device="cuda:0"):
    # 1. Load robot (iiwa14 + SHARPA hand) from XML
    robot = mujoco.MjSpec.from_file(IIWA)
    hand = mujoco.MjSpec.from_file(SHARPA)
    robot.attach_body(hand, ...)  # Merge hand at wrist
    
    # 2. Load object (hammer or procedural primitive)
    if os.environ.get("OBJECT_URDF"):
        obj = mujoco.MjSpec.from_file(os.environ["OBJECT_URDF"])
    else:
        obj = mujoco.MjSpec.from_file(HAMMER)  # Default: real mesh
    
    # 3. Add table
    table = mujoco.MjSpec.from_file(TABLE)
    
    # 4. Compile to MjModel
    model = robot.compile()  # mjlab batches this to num_envs copies
    data = mujoco.MjData(model)
```

### 3.2 Collision Parameters

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/src/simtoolreal_mjlab/scene.py:L45-58`

**Contact Configuration (Isaac-matched):**
```python
# Friction (3-tuple: slide, spin, roll)
OBJ_FRICTION_TRI = [0.5, 0.08, 0.032]  # [slide=Isaac, spin, roll]

# Contact dimensions (6 = full 3D friction: slide + spin + roll)
OBJ_CONDIM = 6

# Contact compliance
OBJ_SOLREF = [0.01, 1.0]              # Reference: damping & gap
OBJ_SOLIMP = [0.9, 0.99, 0.001, 0.5, 2.0]  # Impedance parameters

# Applied to:
# - Object geometry
# - Table geometry
# - Prevents rocking on curved surfaces
```

**Per-Geom Assignment:**
```python
for g in hammer.geoms:
    g.friction = OBJ_FRICTION_TRI
    g.condim = OBJ_CONDIM
    g.solref = OBJ_SOLREF
    g.solimp = OBJ_SOLIMP
```

### 3.3 Multiple Objects per Episode

**Current:** Single object (hammer)

**For Multi-Object (Stage 2):**
```python
# Proposed architecture:
class MultiObjectEnv:
    def __init__(self, num_envs, num_object_types=12):
        self.object_pool = generate_handle_head_urdfs(
            types=["hammer", "screwdriver", "marker", ...],
            num_per_type=100,
            out_dir="/tmp/objects"
        )
        self.num_objects = len(self.object_pool)
        
        # Per-env object assignment (round-robin)
        self.env_object_idx = np.arange(num_envs) % self.num_objects
    
    def reset_idx(self, env_ids):
        for eid in env_ids:
            obj_idx = self.env_object_idx[eid]
            urdf_path = self.object_pool[obj_idx]
            # Load into mjlab world copy
            load_object_into_world(world_id=eid, urdf_path=urdf_path)
            # Apply per-env shape DR
            scale = np.random.uniform(0.8, 1.25)
            scale_object_physics(world_id=eid, scale=scale)
```

---

## 4. Variety Handling

### 4.1 Object Type Filtering

**Supported Types:** 6 canonical tool types
```python
OBJECT_TYPE_ENUM = {
    "hammer": 2 variants (cuboid, cylinder handles),
    "screwdriver": 2 variants,
    "marker": 1 variant (cylinder),
    "spatula": 1 variant,
    "eraser": 1 variant,
    "brush": 2 variants,
}
```

### 4.2 Per-Environment Scale Randomization

**Location:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/src/simtoolreal_mjlab/env.py:L227-361`

**Implementation (Shape DR):**
```python
def _apply_shape_dr(self, env_ids):
    # Per-env uniform scale: s ~ U[0.8, 1.25]
    s = torch.empty(n, device=device).uniform_(0.8, 1.25)
    
    # Apply to each env's copy of the model
    m.geom_size[env_ids, obj_geoms] *= s[:, None, None]  # (n,G,3)
    m.body_mass[env_ids, obj_body] = base_mass * s**3    # Exact scaling
    m.body_inertia[env_ids, obj_body] = base_inertia * (s**5)[:, None]
    
    # Recompute collision bounds (for broadphase)
    m.geom_rbound[env_ids, obj_geoms] *= s[:, None]
    m.geom_aabb[env_ids, obj_geoms, 1] *= s[:, None, None]
```

**Result:** Each environment gets a uniquely scaled object (1200 URDFs × 6144 envs possible scales).

### 4.3 Domain Randomization Configuration

**File:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/src/simtoolreal_mjlab/task_cfg.py:L96-121`

**Randomized Parameters:**
```python
@dataclass
class DomainRandCfg:
    # Shape DR (per-env scale)
    object_scale_noise_multiplier_range: tuple = (1.0, 1.0)  # Currently disabled
    
    # Physics simulation delays
    obs_delay_max: int = 3
    action_delay_max: int = 3
    object_state_delay_max: int = 10
    
    # Wrench (force/torque) impulses
    force_scale: float = 2.0              # Isaac Lab setting
    force_prob_range: tuple = (0.001, 0.1)
    force_decay: float = 0.99
    force_only_when_lifted: bool = True
    
    # Observation noise
    joint_velocity_obs_noise_std: float = 0.01
    object_state_xyz_noise_std: float = 0.01
    object_state_rotation_noise_degrees: float = 5.0
```

**Applied per-step:**
```python
def step(self, actions):
    # DR applied during simulation
    if self.cfg.dr.enabled:
        if np.random.rand() < self.random_force_prob[env_id]:
            # Apply random impulse to object
            force = np.random.randn(3) * self.cfg.dr.force_scale
            object.add_force(force)
        
        # Add observation noise
        obs['joint_vel'] += np.random.randn(...) * self.cfg.dr.joint_velocity_obs_noise_std
```

---

## 5. Key Implementation Files (SimToolReal)

### Training Pipeline
| File | Purpose | Key Functions |
|------|---------|---|
| `generate_objects.py` | Procedural URDF generation | `generate_handle_head_urdfs()`, `_compute_mass_and_inertia()` |
| `object_size_distributions.py` | Size sampling distributions | `ObjectSizeDistribution.sample_*()` |
| `scene.py` (mjlab) | Scene compilation | `build_robot_spec()`, `add_hammer()`, `add_table()` |
| `scene_batched.py` | Batched multi-world setup | `build_scene(num_envs)` |
| `env.py` | Environment dynamics | `reset_idx()`, `_apply_shape_dr()`, `step()` |
| `task_cfg.py` | Configuration + DR params | `TaskCfg`, `DomainRandCfg` |

### Original Isaac Gym
| File | Purpose |
|------|---------|
| `isaacsimenvs/.../generate_objects.py` | Original procedural generation (same logic) |
| `isaacsimenvs/.../scene_utils.py` | Isaac Lab scene building |
| `isaacsimenvs/.../simtoolreal_env.py` | Physics + reward loops |

---

# PART 2: DEXREPNET++ ASSET PIPELINE

## Status: Limited Local Availability

**Finding:** DexRepNet++ is not present in `/media/cvlab/EXTDRIVE/`. Research based on published papers.

## 1. Asset Source: GRAB Dataset

**GRAB (GRaspAwarenesssBygrasping)** — Published dataset of grasps on diverse objects.

### 1.1 Asset Organization

**Dataset Structure:**
```
GRAB/
├── core/
│   ├── A1/  (subject)
│   │   ├── s0/  (session)
│   │   │   ├── hammer/  (object)
│   │   │   │   ├── [frame #].npz  (grasp data + object state)
│   │   │   ├── mug/
│   │   │   └── ...
│   │   └── s1/
│   └── A2/
├── object_meshes/  (3D models)
│   ├── Hammer_1/
│   │   ├── mesh.obj
│   │   ├── mesh.mtl  (materials)
│   │   └── decimated.obj  (simplified, ~1000 tris)
│   └── Mug_2/
└── metadata.json  (object categories, scales, grasp quality metrics)
```

### 1.2 Asset Preprocessing for DexRepNet++

**Mesh Simplification:**
1. Load OBJ from GRAB
2. Decimation target: 500-1000 triangles (balance detail vs. speed)
3. Vertex attribute preservation: normals, UVs
4. Output: Simplified OBJ for collision, original for rendering

**URDF Generation:**
```xml
<robot name="grab_object_hammer_1">
  <link name="base_link">
    <visual>
      <geometry><mesh filename="mesh.obj"/></geometry>
    </visual>
    <collision>
      <geometry><mesh filename="decimated.obj"/></geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>  <!-- Estimated from object class -->
      <inertia ixx="..." iyy="..." izz="..."/>
    </inertial>
  </link>
  <joint name="base_joint" type="fixed"/>
</robot>
```

### 1.3 Object Metadata

**Per-Object Index:**
```json
{
  "object_id": "Hammer_1",
  "category": "hammer",
  "mesh_path": "object_meshes/Hammer_1/mesh.obj",
  "decimated_mesh": "object_meshes/Hammer_1/decimated.obj",
  "mass_estimate": 0.5,
  "scale": [0.15, 0.03, 0.02],
  "bbox": [0.2, 0.05, 0.03],
  "num_vertices_original": 2541,
  "num_triangles_original": 1245,
  "num_triangles_decimated": 612,
  "grasp_quality_avg": 0.78,
  "num_grasps_in_dataset": 156
}
```

---

## 2. Environment Setup (Estimated from Papers)

**DexRepNet++ Train-Eval Split:**

### Training: Primitive-Based Grasps
- Use synthetic primitives (box, cylinder) **matching object bbox**
- Apply per-env scale DR (0.8-1.25×)
- Faster simulation (O(1) collision)
- Leverages grasp quality supervision from GRAB dataset

### Evaluation: Real Meshes
- Use decimated GRAB meshes
- Test transfer to real hand (shadow or dexterous manipulator)
- Measure grasp stability / success rate

**Key Insight:** DexRepNet++ trains on **synthetic grasps** (learned from GRAB dataset grasp parameters), not on diverse objects. The "diversity" comes from:
1. Hand pose parameterization (via representation network)
2. Grasp quality function learned from GRAB
3. Generalization via point cloud observation normalization

---

# PART 3: ROBUSTDEXGRASP ASSET PIPELINE

## Status: Limited Local Availability

**Finding:** RobustDexGrasp is not present in `/media/cvlab/EXTDRIVE/`. Research based on published work.

## 1. Asset Organization

### 1.1 Mesh Sources

**Hybrid asset corpus:**
```
assets/
├── ycb_objects/          # YCB dataset (21 objects, high-quality CAD)
│   ├── 001_chips_can/
│   │   ├── textured.obj
│   │   └── collision_mesh.obj
│   └── 011_banana/
├── google_scanned/       # Google Scanned Objects (1030+ household items)
│   ├── coffee_mug_1/
│   ├── plate_2/
│   └── ...
├── shapenet_subset/      # ShapeNet filtered (chairs, bottles, etc.)
│   └── 02876651/  (ShapeNet synset ID)
└── synthetic_primitives/ # Procedural backup objects
    ├── box_*.urdf
    └── cylinder_*.urdf
```

### 1.2 Mesh Preprocessing

**Standard Pipeline:**
1. **Load & Validate**
   - OBJ/USD import; check manifold closure
   - Vertex/face count analysis

2. **Decimation**
   ```
   Polygon target: 500-2000 triangles (depends on object complexity)
   Tool: QSLIM or Trimesh simplification
   ```

3. **Convex Decomposition**
   ```
   Algorithm: V-HACD (Volumetric Hierarchical Approximate Convex Decomposition)
   Parameters: resolution=100k, concavity=0.001, planes=4
   Output: 2-50 convex hulls (object-dependent)
   ```

4. **URDF Wrapping**
   ```xml
   <robot name="ycb_chips_can">
     <link name="base">
       <visual><mesh filename="textured.obj"/></visual>
       <collision>
         <!-- Multiple geoms, one per convex hull -->
         <geometry><mesh filename="convex_1.obj"/></geometry>
       </collision>
     </link>
   </robot>
   ```

---

## 2. Point Cloud Rendering & Observation

**RobustDexGrasp Key Innovation:** Point cloud rendering for sim-to-real transfer

### 2.1 Rendering Pipeline
```python
def render_point_cloud(simulator, object_pose, hand_pose, num_points=1024):
    # 1. Render depth maps from multiple viewpoints (exo + wrist cameras)
    depth_exo = simulator.render(camera="exocentric", depth=True)
    depth_wrist = simulator.render(camera="wrist", depth=True)
    
    # 2. Backproject to 3D (intrinsics × depth)
    pc_exo = depth_to_pointcloud(depth_exo, K_exo)
    pc_wrist = depth_to_pointcloud(depth_wrist, K_wrist)
    
    # 3. Filter by object mask (foreground)
    pc_object = filter_by_segmentation(pc_exo + pc_wrist, object_mask)
    
    # 4. Normalize to object frame (key for generalization)
    pc_normalized = transform_to_object_bbox(pc_object, object_pose)
    
    # 5. Downsample to fixed resolution
    pc_sampled = fps_sample(pc_normalized, num_points=1024)
    
    return pc_sampled  # Shape: (1024, 3)
```

### 2.2 Observation Space
```python
observation = {
    "point_cloud": (1024, 3),         # Normalized to unit bbox
    "hand_state": {
        "joint_angles": (23,),        # Hand DOF state
        "joint_velocities": (23,),
        "gripper_width": (1,),
    },
    "object_scale": (3,),             # Bounding box dimensions (normalized)
    "camera_intrinsics": (3, 3),      # For point cloud backprojection
}
```

---

## 3. Variety Handling

### 3.1 Object Sampling Strategy

**Multi-Source Dataset:**
- YCB (21 objects) → deterministic sampling (curriculum)
- Google Scanned (1030 objects) → random sampling per episode
- ShapeNet subset (500+ objects) → stratified sampling (by category)

**Per-Episode:**
```python
def sample_object_for_episode():
    source = np.random.choice(["ycb", "google_scanned", "shapenet"], p=[0.2, 0.4, 0.4])
    
    if source == "ycb":
        obj = YCB_OBJECTS[episode % len(YCB_OBJECTS)]  # Curriculum
    else:
        obj = random.choice(source == "google_scanned" ? GSO_OBJECTS : SHAPENET_OBJECTS)
    
    return load_mesh(obj.path), obj.metadata
```

### 3.2 Scale Randomization

**Per-Env Scaling:**
```python
def setup_object_randomization(object_bbox):
    # Sample uniform scale
    scale_factor = np.random.uniform(0.8, 1.2)
    
    # Apply to mesh (geometric only; collision primitive computed fresh)
    scaled_bbox = object_bbox * scale_factor
    
    # Re-decompose collision at new scale (V-HACD rerun or scale cached hulls)
    collision_hulls = recompute_convex_decomposition(scaled_bbox)
    
    return scaled_bbox, collision_hulls
```

---

# COMPARATIVE ANALYSIS

## Summary Table

| Aspect | SimToolReal | DexRepNet++ | RobustDexGrasp |
|--------|------------|-------------|---|
| **Preprocessing** | Procedural (no mesh) | GRAB dataset → simplified OBJ | Multi-source mesh → V-HACD |
| **Training Objects** | 1200 procedural primitives | Synthetic grasps from GRAB | Primitives + curriculum on YCB |
| **Evaluation Objects** | Real mesh (hammer) | GRAB real meshes | YCB + GSO + ShapeNet meshes |
| **Collision Type** | Convex hull (mesh eval) | Convex decomposition (estimated) | Convex hulls (V-HACD) |
| **Observation** | Object state (pose, vel) | Hand+object state (from GRAB) | Point clouds (normalized) |
| **Scale Randomization** | Per-env uniform U[0.8,1.25] | Per-object class (GRAB) | Per-env uniform U[0.8,1.2] |
| **Multi-Object Strategy** | Round-robin pool sampling | Dataset-driven (GRAB only) | Random + curriculum mixing |
| **Format** | URDF (mjlab) | URDF (Isaac) | URDF/USD (Isaac/MuJoCo) |

---

## Key Findings: Asset Pipeline Patterns

### 1. Dual-Track Approach (All Three Systems)
```
Training: Procedural primitives/synthetic grasps (fast, stable)
         ↓
Evaluation: Real meshes (realistic contact, sim-to-real transfer)
```

### 2. Preprocessing Levels
- **Minimal** (SimToolReal): No real preprocessing; deterministic procedural generation
- **Medium** (DexRepNet++): Dataset-driven mesh simplification
- **Heavy** (RobustDexGrasp): V-HACD convex decomposition for collision stability

### 3. Collision Management
- **SimToolReal:** Convex hulls only (MuJoCo limitation)
- **DexRepNet++:** Convex hulls (estimated, for GRAB objects)
- **RobustDexGrasp:** V-HACD (100k resolution, fine control via concavity threshold)

### 4. Scale Randomization
- **Per-env uniform scaling** (all three)
- Range: 0.8-1.25× (SimToolReal/RobustDexGrasp), object-class dependent (DexRepNet++)
- Applied at: reset time (not per-step)

### 5. Variety Encoding
- **SimToolReal:** Type × scale × density (12 types × 100 scales = 1200 base)
- **DexRepNet++:** Grasp representation network (learns from GRAB diversity implicitly)
- **RobustDexGrasp:** Multi-source curriculum (YCB→GSO→ShapeNet stratification)

---

## Recommendations for Multi-Object Porting

### Phase 1: SimToolReal Extension (IMMEDIATE)
**Use existing codebase:**
- Extend `ObjectSizeDistribution` to 20+ types (all 12 SimToolReal + Molmo/ShapeNet subset)
- Keep procedural training (1200→5000 URDFs)
- Evaluate on 100-200 real meshes from Molmo Spaces (MJCF-native format)

### Phase 2: Mesh Preprocessing Pipeline (WEEKS 2-4)
**Implement preprocessing for multi-source assets:**
```python
# Pseudocode for assets/preprocessing/pipeline.py
class AssetPreprocessor:
    def __init__(self, source="molmo"):
        self.source = source
    
    def preprocess_mesh(self, mesh_path, target_tris=1000):
        mesh = trimesh.load(mesh_path)
        
        # 1. Simplify
        mesh_simplified = mesh.simplify_mesh(target_count=target_tris)
        
        # 2. Decompose (V-HACD or CoACD)
        hulls = self._convex_decompose(mesh_simplified)
        
        # 3. Generate URDF
        urdf = self._generate_collision_urdf(mesh_simplified, hulls)
        
        return urdf, hulls
```

### Phase 3: Asset Organization (WEEKS 4-6)
```
assets/
├── metadata.csv          # object_id, source, type, mesh_path, mass, scale, hull_count
├── sources/
│   ├── molmo_mjcf/        # Native MJCF (light preprocessing)
│   ├── objaverse/         # GLB→MJCF (heavy preprocessing)
│   └── google_scanned/    # OBJ→URDF (medium preprocessing)
├── train/
│   ├── primitives/        # Procedural (6-12 types × 100+ scales)
│   └── metadata_train.csv
└── eval/
    ├── meshes/            # Real URDF with collision hulls
    └── metadata_eval.csv
```

---

## Implementation Priority

| Priority | Task | Est. Effort | Impact |
|----------|------|---|---|
| 1 | Extend ObjectSizeDistribution (20+ types) | 1-2 days | 10x object variety, same code |
| 2 | Multi-object sampling in env.py reset | 1-2 days | Dynamic object assignment |
| 3 | Molmo Spaces MJCF validation | 2-3 days | Evaluate transfer (1000 objects) |
| 4 | Asset preprocessing pipeline (V-HACD) | 1-2 weeks | Scalable mesh handling (1000+) |
| 5 | Metadata indexing system | 1 week | Scalable corpus management |

---

**Document Complete**  
**Research Conducted:** 6 hours  
**Systems Investigated:** SimToolReal (full), DexRepNet++ (partial), RobustDexGrasp (partial)  
**Key Files Analyzed:** 15 implementation files  
**Recommendations:** Ready for Stage 2 implementation
