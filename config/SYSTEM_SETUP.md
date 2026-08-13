# System Setup Instructions

This repo is designed to work across multiple systems (DGX, cvlab, personal machines) without hardcoding paths.

## Quick Start (Any System)

### 1. Set MJLAB_PATH environment variable

Before running anything, set the path to your mjlab installation:

```bash
# Add to ~/.bashrc or ~/.zshrc or set for this session only
export MJLAB_PATH="/path/to/mjlab"

# Verify
python -c "import sys; sys.path.insert(0, '$MJLAB_PATH'); import mjlab; print(mjlab.__file__)"
```

### 2. Clone and install

```bash
git clone <this-repo> /path/to/multi_object_porting
cd multi_object_porting
uv venv  # or: python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
uv pip install -e .
```

### 3. Run config check

```bash
python -c "from multi_object_porting.config import cfg; print(cfg.mjlab_path)"
```

---

## System-Specific Setup

### DGX Server (/ihub/homedirs/svs_ald/aditya)

**mjlab location:** `/ihub/homedirs/svs_ald/aditya/simtoolreal_mjlab/mjlab`

```bash
# In your ~/.bashrc or before running experiments:
export MJLAB_PATH="/ihub/homedirs/svs_ald/aditya/simtoolreal_mjlab/mjlab"

# Or create config/dgx.yaml with:
# mjlab_path: "/ihub/homedirs/svs_ald/aditya/simtoolreal_mjlab/mjlab"
```

**GPU Usage Note:** Follow `/ihub/homedirs/svs_ald/use_instructions` to avoid disrupting other users.

### CVLab (/media/cvlab/EXTDRIVE/aditya)

**mjlab location:** `/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/mjlab`

```bash
export MJLAB_PATH="/media/cvlab/EXTDRIVE/aditya/simtoolreal_mjlab/mjlab"
```

### New System

For any new system:
1. Locate your mjlab installation
2. `export MJLAB_PATH="/path/to/mjlab"`
3. Run the config check above

---

## How It Works

The config system loads paths in this order (first match wins):
1. `MJLAB_PATH` environment variable
2. `config/{system_name}.yaml` (if detected)
3. `config/defaults.yaml`

This ensures reproducibility: once you set `MJLAB_PATH`, the code works anywhere.

## Troubleshooting

**"mjlab not found"**
```bash
python -c "import sys; sys.path.insert(0, os.environ.get('MJLAB_PATH', '')); import mjlab"
```

**Wrong path on different system**
Check `python -c "from multi_object_porting.config import cfg; print(cfg)"` and update the environment variable.
