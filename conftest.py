import pathlib
import sys

# Make the repo root importable (llm.py + the redteam package) regardless of pytest's cwd.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
