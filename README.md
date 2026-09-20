# KrishiDrishti: AI-Powered Seasonal Agricultural Intelligence

Data analytics + ML project based on the VOIS AICTE brief *Seasonal Agriculture Performance Analysis*
(brief saved in `docs/project_brief.pdf`).

**Primary USP:** AI/ML prediction + explainability. **Secondary USP:** crop residue intelligence.

## Folder layout
```
data/raw/          original CSV (never edited) + SHA256.txt
data/processed/    cleaned data, created in Phase 2
notebooks/         01..06 notebooks (thin: they call functions in src/)
src/               reusable code (config, data loading, saving helpers, ...)
outputs/figures/   PNG charts
outputs/tables/    CSV tables
outputs/models/    saved models
findings.md        verified findings, updated after each phase
```

## How to run on your computer
```
pip install -r requirements.txt
jupyter notebook          # then open notebooks/01_data_audit.ipynb
```
Notebooks find the project root automatically; run them from inside `notebooks/`.

## Ground rules
No invented numbers. Every finding in `findings.md` carries an evidence label.
Model results are never described as causal. Save helpers refuse to overwrite existing outputs by default.
