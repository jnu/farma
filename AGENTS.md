# AGENTS.md

## Project

Pharmacy access analysis for northern Vermont. Visualizes drive-time gaps
caused by pharmacy closures in rural communities (Caledonia, Orleans,
Lamoille, and Washington counties).

## Stack

### Analysis (current)
- **Python 3.13**, managed with **uv**
- Jupyter notebooks in `notebooks/`
- Key libraries: geopandas, shapely, folium, pandas, numpy, matplotlib, seaborn, scipy
- Input data lives in `data/` (geojson, csv, json).
- Output artifacts that can be regenerated easily should live in `output/`. Some intermediate outputs that need to be cached like large dataframes should be stored in `data`.

### Frontend (planned)
- **SvelteKit** with **TypeScript**, managed with **pnpm**

## Principles

1. **Simplicity above all.** Favor the simplest approach that correctly solves the problem. Avoid abstractions, indirection, or generalization until clearly needed.
2. **Clarity over cleverness.** Code should read like prose. Prefer explicit logic over compact tricks. Name things precisely.
3. **Stay concise.** Remove dead code, unused imports, and stale comments on every pass. Don't leave things around "just in case."
4. **Conservative implementation.** Don't add features, dependencies, or complexity speculatively. When in doubt, leave it out.
5. **Comprehensible analysis.** Notebook cells should tell a clear story. Use markdown cells to explain *why*, not just *what*. Keep cell outputs focused and interpretable.

## Code Style

### Python
- Use type hints for function signatures.
- Prefer f-strings over `.format()` or `%`.
- Keep functions short and single-purpose.
- Use pathlib for file paths.
- Don't add comments that just narrate what the code does. Comments explain *why*.

### Notebooks
- Each notebook should have a clear narrative arc: setup, data loading, analysis, visualization, conclusions.
- Keep cells short. One idea per cell.
- Clean up exploratory/scratch cells before committing.
- Pin any heavy computation outputs to `data/` so notebooks render quickly.

### TypeScript / Svelte (when applicable)
- Prefer `const` over `let`. Never use `var`.
- Use TypeScript strict mode.
- Keep components small and composable.
- Colocate styles with components.

## Dependencies

- **Python:** add via `uv add <package>`. Don't pin versions manually; let `uv.lock` handle resolution.
- **Node (future):** add via `pnpm add <package>`.
- Minimize dependencies. Use the standard library when it suffices.

## Repository Layout

```
notebooks/    # Jupyter analysis notebooks
data/         # Input data and generated outputs (geojson, csv, json, png, html)
```
