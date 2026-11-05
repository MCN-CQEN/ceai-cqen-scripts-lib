"""Compatibility entry point; implementation belongs to the composite action."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[2]
                      / "actions/ghas-prepare-fork/prepare_files.py"), run_name="__main__")
