# Key Assumptions

These are assumptions about systems, data, and requirements. Flag if any prove false.

## System Assumptions

1. **mjlab exists and is accessible**
   - DGX: `/ihub/homedirs/svs_ald/aditya/simtoolreal_mjlab/mjlab`
   - CVLab: `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/mjlab`
   - Assumption: These paths remain stable and mjlab doesn't move
   - Validation: Run `import mjlab; print(mjlab.__file__)` after setting MJLAB_PATH

2. **Python 3.10+ available on both systems**
   - DGX: Check via `python --version`
   - CVLab: Check via `python3 --version`
   - Required for modern type hints, f-strings

3. **uv package manager available** (optional)
   - If not, fall back to `python -m venv` + `pip`

4. **DGX follows use_instructions for GPU usage**
   - Assumption: We respect existing oncall/priority policies
   - Assumption: Won't exceed quota or impact other users

## Data Assumptions

1. **Molmo Spaces has diverse object meshes**
   - Assumption: Can download/access subset of ~1000+ objects
   - Need to verify: License, access requirements, download speed

2. **Mesh objects are usable for training**
   - Assumption: Can import into mjlab (URDF/XML format)
   - Assumption: Collision detection works with complex meshes
   - Question: Do people train with meshes or need simplification?

3. **Primitive objects exist as alternative**
   - Assumption: Simpler shapes (boxes, spheres, cylinders) are available
   - Assumption: Training converges faster with primitives

## Training Assumptions

1. **RL policy needs diverse object shapes**
   - Assumption: Grasping generalizes across similar objects
   - Question: How many objects needed for good diversity?

2. **Existing simtoolreal pipeline is reusable**
   - Assumption: Can adapt hammer/brush training to new objects
   - Assumption: Same observation/action spaces (or close variant)

3. **Molmo benchmark is secondary**
   - Assumption: Stage 1-3 focus on RL training quality
   - Stage 4 (Molmo) uses privileged language info (not in production)

## Constraints

1. **Don't modify outside aditya folder**
   - DGX: Stay in `/ihub/homedirs/svs_ald/aditya/`
   - CVLab: Stay in `/media/cvlab/EXTDRIVE/aditya/`

2. **Disk space is limited**
   - Assumption: Reference mjlab, don't copy
   - Assumption: Assets stored externally or downloaded on-demand

3. **DGX is shared resource**
   - Assumption: Follow use_instructions for GPU time
   - Assumption: Don't run long experiments during peak hours

## Stage 1 Scope Assumptions

1. **Survey is comprehensive, not exhaustive**
   - Will identify 3-5 major asset sources
   - Will review ~10-20 papers on mesh vs. primitive training
   - Will NOT implement anything, only research

2. **Findings will drive Stage 2 design**
   - Assumption: Survey results are actionable
   - Assumption: Can decide on import format/strategy by end of Stage 1

## Validation Checklist

- [ ] mjlab paths work on DGX
- [ ] mjlab paths work on CVLab
- [ ] Python 3.10+ installed on both
- [ ] Can access/download from Molmo Spaces (or alternative source)
- [ ] Existing simtoolreal pipeline documented
- [ ] Mesh import format (URDF/XML) determined
