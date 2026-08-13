# Setup Summary

Created **multi_object_porting** repository at `/media/cvlab/EXTDRIVE/aditya/multi_object_porting`.

## What Was Created

### Architecture and Configuration

✓ **System-agnostic configuration system**
- Environment variable-based path management (`MJLAB_PATH`)
- Config loader in `src/config.py` (auto-detects system)
- Portable across DGX, cvlab, and any future system
- No hardcoded paths in source code

✓ **Project structure** (git-friendly)
```
config/         → Configuration, system setup instructions
docs/           → Documentation and research
src/            → Python source code (minimal for now)
scripts/        → Utility scripts (placeholder)
assets/         → Asset references and organization
experiments/    → Experiment configs and results (not committed)
```

### Documentation and Analysis

✓ **DECISIONS.md** — Architecture decisions with rationale
- Decision 1: MJLAB_PATH environment variable for portability
- Decision 2: Multi-document system for tracking (decisions, assumptions, problems, survey)
- Decision 3: Minimal repo footprint (no vendored deps, reference shared mjlab)
- Decision 4: Stage 1 = Survey only (no implementation)
- Decision 5: No changes outside aditya folder (respect DGX/cvlab boundaries)
- Decision 6: Git-friendly structure (cloneable to any system)

✓ **ASSUMPTIONS.md** — Key assumptions about systems and data
- System assumptions (mjlab paths, Python version, etc.)
- Data assumptions (Molmo availability, mesh usability)
- Training assumptions (diversity, reusability)
- Constraints (disk space, DGX shared resources)
- Validation checklist

✓ **PROBLEMS.md** — Known issues and blockers
- Open issues: Mesh complexity, licensing, import format, pipeline adaptation
- Closed issues: (none yet)
- Research questions for Stage 1 survey

✓ **STAGE1_SURVEY.md** — Comprehensive survey framework
- Research questions (scope and out-of-scope)
- Literature review on mesh vs. primitives (3+ strategic options outlined)
- Asset source comparison (Molmo, ShapeNet, Objaverse, YCB, Google Scanned)
- Mesh complexity analysis and preprocessing strategies
- Import format and asset organization
- Training diversity strategy (preliminary)
- Recommended Stage 2 plan
- Survey progress tracking (TODO items)

### Configuration Files

✓ **config/defaults.yaml** — Default configuration values
✓ **config/SYSTEM_SETUP.md** — Setup instructions for DGX, cvlab, and any new system

✓ **README.md** — Project overview
✓ **.gitignore** — Excludes outputs, logs, venv, OS files

✓ **pyproject.toml** — Minimal dependencies, no mjlab vendoring

## How to Use

### 1. Set Up on Your System (First Time)

```bash
# Identify mjlab path on your system
# DGX: /ihub/homedirs/svs_ald/aditya/simtoolreal_mjlab/mjlab
# CVLab: /media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/mjlab

# Set environment variable (add to ~/.bashrc or ~/.zshrc)
export MJLAB_PATH="/path/to/simtoolreal_mjlab/mjlab"

# Or set temporarily
export MJLAB_PATH="/path/to/simtoolreal_mjlab/mjlab"
```

### 2. Clone and Install

```bash
cd /media/cvlab/EXTDRIVE/aditya  # Or /ihub/homedirs/svs_ald/aditya on DGX

# Create Python environment
uv venv venv  # or: python -m venv venv
source venv/bin/activate  # bash/zsh
# Or: venv\Scripts\activate  (Windows)

# Install package (in editable mode)
uv pip install -e multi_object_porting
```

### 3. Verify Configuration

```bash
python -c "from multi_object_porting.config import cfg; print(cfg)"
```

Should output something like:
```
Config({'repo_root': PosixPath('...'), 'config_dir': PosixPath('...'), 
        'mjlab_path': '/path/to/mjlab', ...})
```

### 4. Start Stage 1: Survey

See `docs/STAGE1_SURVEY.md` for research plan and TODO items.

---

## Key Design Decisions

### Portability
- **MJLAB_PATH**: Instead of copying mjlab (wastes space) or symlinking (breaks across systems), use environment variable.
- **Config system**: Auto-detects system; can also load from `config/{hostname}.yaml`.
- **Relative paths**: Outputs use repo-relative paths; easy to move repo without reconfiguring.

### Documentation
- **Separate concerns**: Decisions (why), Assumptions (what we believe), Problems (blockers), Survey (research).
- **Traceable**: Every decision has rationale. Every problem is actionable. Every assumption is testable.
- **Audit trail**: Future readers can understand "why did we design it this way?"

### Stage 1 Focus
- **Survey only**: No implementation, no porting code yet. Research findings drive Stage 2 design.
- **Comprehensive**: Cover mesh vs. primitives, asset sources, import format, training strategy.
- **Actionable**: Deliver decisions on "what assets to use" and "how to structure the import pipeline."

### Constraints Respected
- **No changes outside aditya**: All work confined to `/media/cvlab/EXTDRIVE/aditya/multi_object_porting` (cvlab) and equivalent on DGX.
- **DGX use_instructions**: Repo structure makes it easy to follow resource policies.
- **Disk efficiency**: Reference shared mjlab; don't duplicate.

---

## Next Steps

1. **Complete STAGE1_SURVEY.md**
   - Research literature on mesh vs. primitives
   - Verify Molmo/ShapeNet/Objaverse access and licensing
   - Decide on preprocessing strategy
   - Document findings

2. **Update PROBLEMS.md**
   - Resolve blockers as they're discovered
   - Move closed issues to separate section

3. **Update ASSUMPTIONS.md**
   - Validate assumptions (run config check on DGX, verify mjlab paths)
   - Fill in validation checklist

4. **Plan Stage 2** (after Stage 1 survey)
   - Asset collection and preprocessing
   - URDF/XML generation pipeline
   - Asset indexing and metadata

---

## File Reference

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `pyproject.toml` | Package metadata and dependencies |
| `.gitignore` | What not to commit |
| `config/SYSTEM_SETUP.md` | How to set up on any system |
| `config/defaults.yaml` | Default configuration |
| `src/config.py` | Python config loader |
| `docs/DECISIONS.md` | Architecture decisions (immutable) |
| `docs/ASSUMPTIONS.md` | Key assumptions (testable) |
| `docs/PROBLEMS.md` | Blockers and open questions |
| `docs/STAGE1_SURVEY.md` | Survey framework and findings |

---

**Created:** Aug 13, 2026  
**Status:** Ready for Stage 1 research  
**Next review:** After STAGE1_SURVEY.md completion  
