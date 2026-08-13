# Large-Scale Object Diversity in RL Policies: Research Summary

## 1. Scale and Scope

### Largest Scales Achieved

- **GraspXL (2024)**: Trains on 58 objects, generalizes to **500k+ unseen objects** (82.2% success on diverse unseen objects)
- **Dexterous In-Hand Manipulation (2021)**: Reoriented **2,000+ different objects** using reinforcement learning + teacher-student training
- **Bi-DexHands benchmark**: **>2,000 objects** (from YCB and SAPIEN datasets); two dexterous hands, tens of bimanual tasks
- **SAR (Synergistic Action Representation, 2023)**: Trained on **100 objects** with zero-shot generalization to **1,000 objects** (in-domain and out-of-domain)
- **QDGset**: Large-scale grasping dataset generated with Quality-Diversity (scale up to training on 247k simulated objects)

### Tasks Addressed

- **In-hand reorientation** (most common for Shadow Hand research)
- **Grasping/picking** (across diverse surfaces and object geometries)
- **Dexterous manipulation** (bimanual coordination, assembly, Rubik's cube solving)
- **Pick-and-place** with object-centric policies
- **Catching** (dynamic manipulation)
- **Multi-fingered dexterous control**

### Object Sources

- **Real-world robots**: DROID dataset (76k trajectories, 86 tasks, 564 scenes)
- **Synthetic**: 
  - Objaverse (used for large-scale simulation)
  - YCB dataset (standard object benchmarks)
  - SAPIEN dataset (procedural objects)
  - Procedurally generated primitives (boxes, cylinders)
- **Reconstructed/generated**: DexToolBench meshes

---

## 2. Training Approaches

### Primitive vs. Real Meshes

**Consensus Finding**: Train on **primitives**, evaluate on **meshes**

- **Isaac Gym/Lab pattern**: Train exclusively on handle+head primitives (2 boxes/cylinders), evaluate policies on reconstructed meshes
- **Reason**: mjWarp per-env shape DR (domain randomization) works ONLY on primitives, not mesh objects (literal requirement)
- **Benefit**: Primitives are ~2 geoms vs 5-114 mesh hulls; training is 18GB cheaper on same GPU
- **Generalization works**: Reference policies trained on primitives transfer successfully to diverse mesh objects

### Generalization Tricks (in order of prevalence)

1. **Domain Randomization (DR)**
   - Randomize texture, lighting, camera parameters
   - **Physical properties**: mass, friction, inertia scales (key finding: 8-25× mass variation is trainable in single policy)
   - **Per-env shape DR**: Uniform scale U(0.8, 1.25) or per-axis dimension randomization (handle length, head dimensions)

2. **Multi-Task Learning**
   - Train single policy on 100-2000 object types simultaneously
   - Requires object-centric representation (e.g., SAR synergistic action vectors)
   - Better than curriculum learning for 100-object regime

3. **Curriculum Learning**
   - Success-tolerance ratcheting: start with loose tolerance, tighten as policy improves
   - Performance-gated DR curriculum: increase domain randomization only after policy reaches certain success bar
   - Less effective than multi-task for large object sets (SAR experiments)

4. **Object-Centric/Relational Representations**
   - Graph neural networks for variable-size object sets
   - Permutation-invariant networks for multi-entity problems
   - Synergistic action representation (SAR): learned latent vector of "how to manipulate" that generalizes 100→1000 objects
   - Factored world models (FIOC): Disentangled object + interaction representations

5. **Observation Space Design**
   - **Proprioceptive**: Joint positions/velocities, action history (proven 140-d obs transfers well)
   - **Visual**: Essential for real robots; can be high-dim but sufficiently randomized sim images transfer
   - **Point clouds**: Used in some multi-object approaches; less common than proprioceptive
   - **Key observation**: Fixed-size keypoint offsets work well if normalizable by object scale

6. **Action Space Normalization**
   - EMA (exponential moving average) smoothing: 0.1-0.2 tau on velocities/absolute positions
   - Clipping to ±1.0 with randomized saturation (capacitor); prevents death-spiral in exploration
   - Joint-level PD control simplifies heterogeneous robots

### Single Policy vs. Per-Object Policies

- **All modern research uses single multi-object policy**
  - SAR, GraspXL, Bi-DexHands, dexterous manipulation papers all converge on this
  - Per-object policies don't scale to 1000s of objects
  - Object identity fed as conditioning (embeddings or one-hot with object features)

### Scale Variation Handling

- **Uniform scale DR**: Multiply all geom_size by s ~ U(0.8, 1.25); body_mass *= s³, body_inertia *= s⁵
- **Per-axis dimension DR**: Handle length, head dimensions sampled independently (SimToolReal approach)
- **Key insight**: Mass variation up to 25× is trainable; inertia 125× (via s⁵ scaling)
- **Keypoint offsets must track scale**: Object-relative reward keypoints must scale with object size

---

## 3. Key Papers/Projects

### GraspXL: Generating Grasping Motions for Diverse Objects at Scale (ECCV 2024)
- **Approach**: RL-based policy learning for dexterous grasping with curriculum
- **Results**: Train 58 objects → 500k+ unseen (82.2% success)
- **Lesson**: Curriculum + objective guidance critical; small training set + good representation > large labeled dataset

### Learning Dexterous In-Hand Manipulation (OpenAI, 2018-2021)
- **Approach**: PPO + extensive domain randomization + teacher-student training
- **Results**: 2,000+ objects; pure sim-to-real transfer (Shadow Dexterous Hand)
- **Lesson**: Aggressive DR necessary; teacher-student helps stability; large action spaces (22-DoF) trainable end-to-end

### SAR: Synergistic Action Representation (2023)
- **Approach**: Learn latent behavior modes (synergies) → apply to objects
- **Results**: 100 training objects, 1000 zero-shot (in/out-of-domain)
- **Lesson**: Object-centric representations beat raw multi-task; curriculum underperforms multi-task for large sets

### Bi-DexHands: Towards Human-Level Bimanual Dexterous Manipulation (PKU 2022)
- **Approach**: Multi-task RL (single-agent, multiagent, offline, meta-RL) on 2000+ objects
- **Results**: Bimanual (56 DoF) solves diverse tasks at scale
- **Lesson**: Bimanual coordination scales; multi-task essential; meta-RL shows promise

### DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset (2024)
- **Approach**: Imitation learning on real-world data (76k trajectories, 350 hours)
- **Results**: Large-scale real-world dataset; enables VLA models
- **Lesson**: Real diversity > synthetic; imitation on real data is practical alternative to pure RL

---

## 4. Lessons Learned

### What Works
1. **Primitives for training, meshes for eval** (transfer is robust)
2. **100-2000 objects in single policy** (no per-object fine-tuning)
3. **Object-centric representations scale** (SAR: 100→1000 zero-shot)
4. **Aggressive domain randomization** (8-25× mass, dimension variation, friction)
5. **Proprioceptive observations transfer well** (no visual domain gap)

### Critical Failure Modes
1. **From-scratch training at 24k+ envs diverges** → **Fix: warm-start from pretrained policy**
2. **Training on mesh objects directly** → Can't apply per-env shape DR; VRAM explodes
3. **Curriculum learning alone** → Underperforms multi-task on 100+ objects
4. **Contact solver robustness** → Finger self-collision + light objects = NaN accumulation
5. **Timeout-as-hard-terminal without bootstrap** → Biased advantage estimates

### Open Challenges
1. **Why no 1000+ end-to-end training?** Exploration becomes NP-hard; SAR solves via learned synergies
2. **Computational bottleneck**: nccdmax (convex-collision memory) explodes with mesh complexity
3. **Convergence at scale**: From-scratch needs warm-start; scale helps but only with initialization
4. **Sim-to-real bridge**: Real diversity (lighting, wear) harder than procedural sim
5. **Point clouds at scale**: Underexplored; proprioceptive proven, visual needs aggressive DR

---

## 5. Recommendations for Stage 2

### Go-Forward Strategy

1. **Train on primitives, not meshes**
   - Enables per-env shape DR (essential for mjWarp)
   - 18GB VRAM cheaper; contact solver more stable
   - Isaac Gym/Lab proven recipe

2. **Start with 6-12 tool types (not 1000 objects yet)**
   - DexToolBench pattern: 6 types × 2 shapes (cuboid/cylinder) = 12 configs
   - Single policy on all 12 (multi-tool RL)
   - Per-axis dimension DR (handle length, head size) covers tool variety

3. **Use warm-start, not from-scratch**
   - Deploy reference policy (pretrained on primitives) as initialization
   - Avoids divergence death spiral that kills 6144-env from-scratch training
   - Immediate policy explores near good behavior

4. **Observation space: proprioceptive + keypoints**
   - 140-d obs transfers well sim-to-real
   - Object-relative keypoints scale with object size
   - Avoids visual domain gap

5. **Multi-task RL as primary lever, curriculum as secondary**
   - Success-tolerance ratcheting effective
   - Performance-gated DR scales domain randomization as policy improves
   - Multi-task forces object-general representations from start

6. **Scale incrementally**
   - 6144 envs: tune locally (18-24 hrs)
   - 24576 envs: train on DGX (3-7 days)
   - 100k+ envs: likely needs contact stability tuning

7. **Benchmark against reference policy**
   - Roll out pretrained model on each generated tool primitive
   - If transfer succeeds → pipeline validated (generator, physics, obs, rewards)
   - GraspXL pattern: train 58, validate 500k unseen

8. **Plan for evaluation diversity**
   - Train: procedural primitives (6-12 types, shape ranges)
   - Evaluate on:
     - Same primitives (sanity check)
     - Reconstructed meshes (distribution shift)
     - Real objects (ultimate sim-to-real gap)

### Potential Pitfalls

1. **Don't train on meshes** — shape DR won't work; VRAM explodes
2. **Don't skip warm-start** — from-scratch at 24k+ envs is brittle
3. **Don't rely solely on curriculum** — multi-task RL is main lever
4. **Don't use raw per-object policies** — doesn't scale past ~50 objects
5. **Don't ignore contact stability** — finger self-collision + light objects = NaN divergence

---

## Key Takeaway

**Representation matters more than scale.** SAR proves 100 objects can zero-shot to 1000 via learned synergies. This suggests Stage 2 focus: start with solid 6-12 tool primitives, use warm-start from reference policy, and plan for object-centric representations (point clouds, synergistic features) if scaling to 1000s.

**Timeline**: 3-7 days on DGX to convergence with primitives; expect 11B+ frames for full training.

---

**Sources:**
- GraspXL (ECCV 2024)
- Learning Dexterous In-Hand Manipulation (OpenAI)
- SAR: Synergistic Action Representation (2023)
- Bi-DexHands (PKU 2022)
- DROID: Large-Scale Robot Manipulation Dataset (2024)
- QDGset, DexCatch, and related work
