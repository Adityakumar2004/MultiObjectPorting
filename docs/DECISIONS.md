# Architecture Decisions

## Decision 1: Environment Variable-Based Configuration (MJLAB_PATH)

**Status:** DECIDED

**Context:** mjlab exists in `simtoolreal_mjlab` on both DGX and cvlab, but at different absolute paths. Duplicating it would waste space; copying it to each new repo breaks maintainability.

**Decision:** Use `MJLAB_PATH` environment variable + auto-detection system to reference external mjlab.

**Rationale:**
- Scales to any number of systems without code changes
- No hardcoded paths in source code or config files
- Clear, explicit setup step per system
- Falls back to defaults if not set
- Works with git cloning to new systems

**Rejected alternatives:**
- Symlinks: Fragile across systems with different mount points
- Git submodule: Complicates repo, mjlab is large and external
- Copying mjlab: Wastes disk space, duplicates maintenance burden
- Hardcoded paths: Breaks reproducibility

**Implementation:**
- `config.py`: Loads from env > system config > defaults
- `config/SYSTEM_SETUP.md`: Clear instructions per system
- `config/defaults.yaml`: Fallback values

---

## Decision 2: Multi-Document System for Analysis

**Status:** DECIDED

**Context:** Need to track survey findings, architectural decisions, assumptions, and problems in organized way.

**Decision:** Separate documents for each concern type:
- `DECISIONS.md` — Architecture/design decisions (this file)
- `ASSUMPTIONS.md` — System assumptions and constraints
- `PROBLEMS.md` — Known issues and blockers
- `STAGE1_SURVEY.md` — Research findings for Stage 1

**Rationale:**
- Each document serves different purpose; easier to maintain
- Decisions are immutable (record why we chose X)
- Assumptions are testable (can be validated/refuted)
- Problems are actionable (can be resolved)
- Survey is time-bounded (specific to Stage 1)
- Clear audit trail for design decisions

---

## Decision 3: Minimal Repo Footprint

**Status:** DECIDED

**Context:** Repo will be cloned to DGX and cvlab; disk usage matters, GPU usage affects other users.

**Decision:**
- No vendored dependencies beyond pyproject.toml
- Reference existing mjlab via path variable
- No training outputs committed to git (use .gitignore)
- Code-only repo: docs, scripts, config, no data/weights

**Rationale:**
- Respect shared resource usage on DGX
- Fast clones to any system
- Clear git history without binary bloat
- Outputs/logs managed locally, not in version control

---

## Decision 4: Stage 1 = Survey Only

**Status:** DECIDED

**Context:** User requested Stage 1 = research on asset availability, sources, mesh vs. primitives, etc.

**Decision:** Stage 1 deliverable is comprehensive survey document + findings. No implementation/porting code yet.

**Rationale:**
- Validate assumptions before building
- Identify best asset sources (Molmo Spaces vs. alternatives)
- Understand mesh/primitive tradeoffs from literature
- Decide on porting strategy based on findings
- Minimize wasted effort on wrong approach

**Next stages** (post-Stage 1):
- Stage 2: Implement asset import pipeline based on survey findings
- Stage 3: Train RL policy with imported assets
- Stage 4: Benchmark on Molmo (with privileged language info)

---

## Decision 5: No Changes Outside aditya Folder

**Status:** CONSTRAINT

**Context:** User explicitly requested not to modify files outside `/media/cvlab/EXTDRIVE/aditya` (cvlab) or `/ihub/homedirs/svs_ald/aditya` (DGX).

**Implementation:**
- All work confined to `multi_object_porting` subfolder
- No global env var changes, no system config modifications
- Users explicitly set `MJLAB_PATH` if needed
- Respects DGX use_instructions: no disruption to other users

---

## Decision 6: Git-Friendly Structure

**Status:** DECIDED

**Context:** Repo will be pushed to GitHub and cloned to multiple systems.

**Decision:**
- No system-specific .gitignore exceptions
- Standard Python project layout
- Clear documentation for each system's setup
- Config files are examples, not system-dependent

**Rationale:**
- Anyone can fork and clone without system knowledge
- Reproducible across personal machines, labs, clusters
- No accidental commits of local paths

---

## TODO Decisions

These will be decided during Stage 1 survey:
- [ ] Asset source priority: Molmo Spaces vs. other sources?
- [ ] Mesh handling: decimation strategy, collision complexity
- [ ] Import format: URDF vs. XML vs. custom importer?
- [ ] Asset organization: by source? by category? by size?
- [ ] Training data format: what observation/action spaces for diversity?
