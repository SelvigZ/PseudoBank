"""
PseudoBank Configuration

Simple settings for the pseudonymization tool.
"""

from pathlib import Path

# =============================================================================
# FOLDER SETTINGS
# =============================================================================
# These are relative to the PseudoBank project folder

PROJECT_ROOT = Path(__file__).parent.parent

INPUT_FOLDER = PROJECT_ROOT / "sample_data"
OUTPUT_FOLDER = PROJECT_ROOT / "output"
