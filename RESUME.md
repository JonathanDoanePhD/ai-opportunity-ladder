# How to resume the pipeline

Run from this project folder.

1. **Rebuild inputs if the container is new** (`data/raw/` and `data/interim/` are not committed):
   `python3 -I scripts/fetch_data.py .`, then `python3 -I scripts/01_make_batches.py`
   (deterministic) and `python3 -I scripts/02_build_occupations.py`.
2. **Pending:** `python3 -I scripts/status.py --json`.
3. **Rate:** launch `scripts/workflows/rate.js` with
   `args: {"main": [<pending main batches>], "reference": [<pending reference batches>]}`.
   The main pass uses Sonnet; the reference pass uses the default model.
4. Then `python3 -I scripts/03_reliability.py` and `python3 -I scripts/04_analysis.py`. Commit
   `data/coded/` and `output/` after each wave (never `data/raw/` or `data/interim/`).
