"""Configuration loader for multi_object_porting.

Loads system-specific paths from environment variables and YAML configs.
Priority: env vars > system config > defaults
"""

import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Configuration object with defaults and system-specific overrides."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.config_dir = self.repo_root / "config"

        # Load defaults
        self._load_defaults()

        # Override with system-specific config if found
        self._load_system_config()

        # Override with environment variables
        self._load_env_vars()

    def _load_defaults(self):
        """Load config/defaults.yaml."""
        defaults_file = self.config_dir / "defaults.yaml"
        if defaults_file.exists():
            with open(defaults_file) as f:
                defaults = yaml.safe_load(f) or {}
        else:
            defaults = {}

        # Set attributes from defaults
        for key, value in defaults.items():
            setattr(self, key, value)

    def _load_system_config(self):
        """Load system-specific config if available."""
        # Try to detect system
        hostname = os.uname().nodename
        system_config_file = self.config_dir / f"{hostname}.yaml"

        if system_config_file.exists():
            with open(system_config_file) as f:
                overrides = yaml.safe_load(f) or {}
            for key, value in overrides.items():
                setattr(self, key, value)

    def _load_env_vars(self):
        """Override with environment variables."""
        if mjlab_path := os.environ.get("MJLAB_PATH"):
            self.mjlab_path = mjlab_path

    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return f"Config({attrs})"


# Global config instance
cfg = Config()
