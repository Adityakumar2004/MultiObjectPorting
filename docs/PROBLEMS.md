# Known Problems and Blockers

Track issues discovered during development. Resolve and move to closed section.

## Open Issues

### Problem 1: Mesh Complexity in Simulation
**Severity:** MEDIUM (blocks Stage 2)

**Description:** Unclear if complex meshes (high polygon count) can be trained with efficiently.

**Impact:** If meshes are too slow, may need to:
- Decimation pipeline to reduce complexity
- Use primitives for training, mesh for eval
- Find pre-simplified asset sources

**Blocked by:** Survey findings (Stage 1)

---

### Problem 2: Asset Source Licensing
**Severity:** MEDIUM (blocks Stage 2)

**Description:** Unclear what license restrictions apply to Molmo Spaces or alternative asset sources.

**Impact:** May not be able to use certain sources for training or publication.

**Action:** Survey should check licensing for each source.

---

### Problem 3: mjlab Import Format
**Severity:** MEDIUM (blocks Stage 2)

**Description:** Which formats does mjlab support? URDF? XML? OBJ?

**Impact:** Determines asset preprocessing pipeline complexity.

**Action:** Check mjlab docs and existing simtoolreal code.

---

### Problem 4: Existing simtoolreal Pipeline Adaptation
**Severity:** LOW (doesn't block survey)

**Description:** Can we reuse observation/action spaces from hammer/brush training?

**Impact:** If not, need to design new spaces (extra work).

**Action:** Document existing pipeline structure in Stage 1.

---

## Closed Issues

(None yet)

---

## Questions for Stage 1 Survey

These are open research questions, not blockers:

1. **Mesh vs. Primitives**: How do practitioners handle mesh complexity?
   - Do they decimate meshes?
   - Train on primitives, eval on mesh?
   - Use physics-aware simplification?

2. **Asset Diversity**: How many objects needed for good generalization?
   - 10? 100? 1000+?
   - What makes objects "diverse" for grasping?

3. **Asset Sources**: What's the best source for multi-object grasping?
   - Molmo Spaces (large, diverse)
   - ShapeNet (CAD models, well-structured)
   - Objaverse (internet-scale, inconsistent quality)
   - Custom collections (YCB, Amazon Picking, etc.)

4. **Import Pipeline**: What preprocessing is typical?
   - Scale normalization?
   - Collision primitive creation?
   - Texture/material handling?

5. **Training Diversity**: How to structure training for good generalization?
   - Random object sampling?
   - Curriculum learning (simple → complex)?
   - Size/shape constraints?
