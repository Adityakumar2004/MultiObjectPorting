# Stage 1: Asset Source and Import Strategy Survey

**Status:** IN PROGRESS (Aug 2026)

**Goal:** Research and document asset sources, mesh vs. primitive tradeoffs, and plan Stage 2 import pipeline.

**Deliverables:**
- [ ] Literature review: Mesh vs. primitives in simulation-based RL
- [ ] Asset source comparison (Molmo, ShapeNet, Objaverse, etc.)
- [ ] Mesh complexity analysis and handling strategies
- [ ] Recommended import format and pipeline
- [ ] Stage 2 plan based on findings

---

## 1. Scope and Research Questions

### Primary Questions

1. **What asset sources can provide 1000+ diverse objects for grasping RL?**
   - Availability (number, diversity)
   - Cost/effort to access (licensing, download, preprocessing)
   - Quality and compatibility with mjlab

2. **Can we train effectively with complex meshes, or do we need primitives?**
   - Mesh complexity impact on simulation speed
   - Impact on RL convergence
   - Mesh simplification strategies (decimation, collision primitives)

3. **What import format and preprocessing is typical in the field?**
   - URDF vs. XML vs. custom formats
   - Common preprocessing (scaling, COM adjustment, collision setup)
   - Tools/pipelines used by other researchers

4. **How should we structure multi-object training for good generalization?**
   - Asset sampling strategy (random, curriculum, balanced)
   - Observation/action space considerations for diversity
   - Expected training time and sample efficiency

### Out of Scope (for Stage 1)
- Actual implementation or code
- Training data collection
- RL policy architecture design
- Molmo benchmark integration (Stage 4)

---

## 2. Literature Review: Mesh vs. Primitives

### 2.1 Simulation-Based RL and Mesh Complexity

**Key Insight:** Most simulation-based RL uses *primitive* shapes, not complex meshes. Reasons:

1. **Simulation Speed**
   - Primitive collision detection: O(1) or O(log n) for convex shapes
   - Mesh collision: O(n) to O(n log n) depending on algorithm and mesh complexity
   - RL requires 100k-1M+ steps; mesh simulation can 10-100x slower per step
   - **Impact:** Infeasible training times for large-scale RL

2. **Stability and Robustness**
   - Primitive shapes: Well-defined, stable collision response
   - Complex meshes: Numerical instabilities, surface artifacts, interpenetration
   - Degenerate triangles, non-manifold geometry cause simulation errors
   - **Impact:** Training divergence, unpredictable behavior

3. **Common Practice**
   - Most robot learning papers use:
     - YCB objects (CAD models, but often approximated with primitives)
     - ShapeNet models (decimated, simplified for collision)
     - Procedurally generated primitives (boxes, cylinders, random shapes)
   - **Few use raw meshes** (those that do: heavy preprocessing)

### 2.2 Mesh Handling Strategies in the Field

**Strategy 1: Decimation + Collision Simplification**
- Reduce polygon count (target: 100-500 triangles per object)
- Create convex collision primitives from mesh (hull approximation)
- Render with full mesh, collide with simplified primitive
- **Example:** Used in some Manopla/dexterity papers

**Strategy 2: Primitive Approximation**
- Decompose mesh into convex parts
- Replace with bounding boxes/capsules/spheres
- Fits well for simple objects (tool-like: hammers, brushes, cups)
- **Example:** SimToolReal (your existing pipeline likely does this)

**Strategy 3: Mesh → Training Curriculum**
- Start with primitives for training
- Test final policy on full mesh (sim-to-real transfer)
- **Rationale:** Training is easier; testing is harder (more realistic)
- **Example:** Some dexterity papers (e.g., DDPG for hand manipulation)

### 2.3 Key References (Survey Points)

To complete this section, will review:
- [ ] Sim-to-real transfer papers (Do meshes matter for real-world performance?)
- [ ] Object manipulation benchmarks (Which use meshes? Which use primitives?)
- [ ] Physics engine comparisons (MuJoCo, Bullet, Isaac) and their mesh handling
- [ ] Recent diffusion-based manipulation papers (do they use meshes?)

**Research direction:** Check recent papers on object grasping/manipulation with RL (2024+) to see current practice.

---

## 3. Asset Source Comparison

### Candidates for Multi-Object Grasping RL

#### 3.1 Molmo Spaces
**Pros:**
- Massive scale (1000s of diverse objects)
- High-quality scans or models
- Good coverage of everyday objects

**Cons:**
- Need to verify access/licensing for RL training
- Mesh quality/complexity unknown
- Would need preprocessing for mjlab

**Relevance:** High (explicitly mentioned in requirements; benchmark at end)

**Status:** [ ] Need to check access, licensing, mesh quality

---

#### 3.2 ShapeNet
**Pros:**
- Well-curated CAD models (57k models)
- Structured by category (furniture, tools, vehicles, etc.)
- Commonly used in robotics papers (YCB subset, ScanNet)
- Open access (with attribution)

**Cons:**
- Smaller scale than Molmo
- CAD models may need realism adjustment
- Polygon counts vary widely

**Relevance:** HIGH (established standard in robotics)

**Status:** [ ] Check polygon counts, category coverage for grasping

---

#### 3.3 Objaverse
**Pros:**
- Internet-scale diversity (800k+ objects)
- Includes scans and CAD models
- Free access (ODCC license)

**Cons:**
- Quality highly variable (internet data)
- Many objects not graspable (scenes, buildings, text)
- Heavy preprocessing needed

**Relevance:** MEDIUM (diversity is good; quality is risky)

**Status:** [ ] Assess filtering/quality control needed

---

#### 3.4 YCB Object Set
**Pros:**
- Designed for manipulation research
- Well-documented, tested with real robots
- CAD models available in multiple formats
- Small but high-quality (21 objects)

**Cons:**
- Limited scale
- Doesn't provide diversity needed for 1000+ object RL

**Relevance:** LOW (too small, but good for validation)

**Status:** [x] Known; useful for validation/testing only

---

#### 3.5 Google Scanned Objects
**Pros:**
- High-quality scans of real objects
- Large scale (over 1000 objects)
- Realistic geometries

**Cons:**
- Scans may have noise/artifacts
- Complex meshes
- Licensing restrictions (academic use only)

**Relevance:** MEDIUM (good quality; unclear licensing)

**Status:** [ ] Check licensing and mesh complexity

---

### Comparison Table

| Source | Scale | Quality | Meshes | Preprocessing | Access | For Grasping |
|--------|-------|---------|--------|---|---|---|
| Molmo Spaces | 1000s | High | Yes | Heavy | Verify | ✓ (explicit target) |
| ShapeNet | 57k | High | CAD | Medium | Free | ✓ (established) |
| Objaverse | 800k | Variable | Mixed | Very Heavy | Free | ✓ (with filtering) |
| YCB | 21 | Very High | CAD | Light | Free | ✓ (validation only) |
| Google Scanned | 1000+ | High | Yes | Heavy | Restricted | ? (verify access) |

---

## 4. Mesh Complexity and Preprocessing Strategy

### 4.1 Polygon Count Guidelines

**For mjlab simulation:**
- **Light:** 100-500 triangles → ~1ms collision check, stable
- **Medium:** 500-2000 triangles → ~5-10ms, acceptable for training
- **Heavy:** 2000+ triangles → 20-100ms+, too slow for RL
- **Extreme:** 10k+ triangles → infeasible for real-time training

**For typical objects:**
- YCB CAD models: 500-5000 triangles (mixed)
- ShapeNet models: 1000-50k triangles (wide range)
- Molmo Spaces: Unknown, needs survey
- Google Scanned: 10k-100k triangles (complex)

### 4.2 Preprocessing Pipeline Options

**Option A: Decimation Only**
```
Raw mesh → Decimation (target 500 tris) → mjlab URDF → Train
```
- Pros: Simple, fast preprocessing
- Cons: Loses detail; may hurt visual realism

**Option B: Hybrid Collision**
```
Raw mesh → Decimation (rendering) + Convex Hull/AABB (collision) → mjlab URDF → Train
```
- Pros: Realistic rendering, fast collision
- Cons: Unrealistic contact response (collision doesn't match visuals)

**Option C: Primitive Approximation**
```
Raw mesh → Analyze shape → Generate primitives (boxes/capsules) → mjlab URDF → Train
```
- Pros: Fastest, most stable
- Cons: Loses geometric detail

**Option D: Selective Meshes**
```
Analyze mesh complexity → Keep light meshes, approximate heavy ones → Pipeline per object
```
- Pros: Balances efficiency and realism
- Cons: Complex preprocessing, per-object tuning

### 4.3 Recommendation (Pending Survey)

**Current hypothesis:** Option D (selective) is most flexible. Start with decimation only; switch to primitives if too slow.

---

## 5. Import Format and Pipeline

### 5.1 mjlab Supported Formats

**Status:** [ ] Verify with mjlab documentation and simtoolreal code

**Likely formats:**
- URDF (Unified Robot Description Format) — standard in ROS
- MuJoCo XML — native to MuJoCo (underlies mjlab)
- OBJ → converted to URDF/XML

### 5.2 Asset Organization Structure

**Planned structure:**
```
assets/
├── metadata.csv          # Index: object_id, source, category, poly_count, etc.
├── sources/
│   ├── shapenet/
│   │   ├── 02942699/     # Category ID (cups)
│   │   └── ...
│   ├── molmo/
│   │   ├── obj_001/
│   │   └── ...
│   └── ...
└── processed/
    ├── urdf/             # Converted to URDF
    ├── mesh_simplified/  # Decimated meshes
    └── metadata.jsonl    # Rich metadata per object
```

**Metadata fields per object:**
- object_id, source, source_id
- category, graspability_estimate
- polygon_count (raw, simplified)
- scale (mm, cm, or normalized)
- dimensions (bounding box)
- collision_type (mesh, convex_hull, primitive)
- sim_feasibility (fast, medium, slow)

---

## 6. Training Diversity Strategy (Preliminary)

### 6.1 Object Sampling

**Hypothesis:** Random sampling from 1000+ diverse objects should provide good generalization.

**Questions to resolve:**
- [ ] Should we stratify by category? (10% cups, 10% tools, etc.)
- [ ] Curriculum learning: simple → complex?
- [ ] How many objects per episode? (one? random subset?)

### 6.2 Observation Space

**Current simtoolreal observation (assumed):**
- Object state: position, orientation, velocity
- Gripper state: position, finger angle, force
- Visual: point cloud or RGB

**For diverse objects:**
- Normalize scales? (makes small/large objects look similar)
- Include object properties? (size, mass, friction estimates)
- Augment with object features? (convexity, symmetry)

### 6.3 Action Space

**Assumed current:** End-effector actions (position, rotation, force)

**For diverse grasping:**
- May need to normalize w.r.t. object scale
- Or train scale-invariant policy
- Or per-object scaling (meta-learning style)

---

## 7. Recommendations and Next Steps

### 7.1 Recommended Stage 2 Plan (Preliminary)

1. **Collect and process assets:**
   - Start with ShapeNet (known quality, established)
   - Add Molmo Spaces if access/licensing clear
   - Subset to ~500-1000 graspable objects

2. **Preprocessing pipeline:**
   - Implement decimation (target 500-1000 triangles)
   - Automatic URDF generation
   - Metadata indexing (category, complexity, etc.)

3. **Training setup:**
   - Adapt simtoolreal pipeline to sample objects randomly
   - Verify convergence on small object set first (~10 objects)
   - Scale to full set

4. **Validation:**
   - Test on YCB objects (known good)
   - Benchmark on diverse unseen objects
   - Early Molmo evaluation (with privileged language info)

### 7.2 Open Questions (To Research)

Priority 1 (blocks Stage 2):
- [ ] Mesh vs. primitives: What's the field doing? (literature)
- [ ] Molmo access: Can we download/use? What's the licensing?
- [ ] mjlab format: URDF or XML? What's easiest?

Priority 2 (shapes Stage 2 design):
- [ ] How to normalize object scales in observations?
- [ ] Does curriculum learning help with diverse objects?
- [ ] How many objects needed for good generalization?

Priority 3 (optimization):
- [ ] Best mesh decimation algorithms/tools?
- [ ] Convex hull generation from meshes?
- [ ] Batch URDF generation tools?

---

## 8. Survey Progress

| Item | Status | Notes |
|------|--------|-------|
| Literature review (mesh vs. primitives) | TODO | Need to research |
| ShapeNet analysis | TODO | Check poly counts, categories |
| Molmo access verification | TODO | Check licensing, access |
| Objaverse quality assessment | TODO | Filtering strategy? |
| mjlab format research | TODO | Check docs + simtoolreal code |
| Preprocessing strategy decision | TODO | Pending mesh complexity findings |
| Asset organization design | IN PROGRESS | Outlined structure above |
| Training diversity strategy | TODO | Needs more research |

---

## References (To Populate)

- [ ] Sim-to-Real Transfer learning papers
- [ ] Object manipulation benchmarks (SAPG, MuJoCo Menagerie, etc.)
- [ ] Physics engine comparisons
- [ ] Recent grasping/dexterity papers (2023-2025)
- [ ] Asset sources documentation (ShapeNet, Molmo, Objaverse)
- [ ] mjlab and simtoolreal codebase

---

## Author's Notes

**Created:** Aug 13, 2026

**Next steps:** Fill in [TODO] sections above. This survey should be comprehensive but actionable—not exhaustive literature review, but enough to make informed Stage 2 decisions.
