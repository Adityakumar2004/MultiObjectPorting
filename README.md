# multi_object_porting

Multi-object asset porting and RL grasping policy training pipeline. Designed to work across multiple systems (DGX, cvlab, etc.) without hardcoding paths.

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

See `config/SYSTEM_SETUP.md` for system-specific instructions.

## Structure

- `config/` — Configuration files and system setup
- `docs/` — Documentation, surveys, decisions, analyses
- `src/` — Python source code
- `scripts/` — Utility scripts
- `assets/` — Asset references and management
- `experiments/` — Experiment configurations and results

## Stage 1: Asset Source Survey

Goal: Identify available asset sources, understand mesh vs. primitive training tradeoffs, and plan import strategy.

See `docs/STAGE1_SURVEY.md` for progress.

## Documentation

Key documents:
- `docs/DECISIONS.md` — Architecture decisions and rationale
- `docs/ASSUMPTIONS.md` — Key assumptions about systems and data
- `docs/PROBLEMS.md` — Known issues and blockers
- `docs/STAGE1_SURVEY.md` — Stage 1 research findings

## System-Specific Notes

### DGX
- MJLAB_PATH: `/ihub/homedirs/svs_ald/aditya/simtoolreal_mjlab/mjlab`
- Follow `/ihub/homedirs/svs_ald/use_instructions` for GPU usage

### CVLab
- MJLAB_PATH: `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/mjlab`
