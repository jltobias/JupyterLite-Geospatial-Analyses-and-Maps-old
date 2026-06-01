# JupyterLite Maps and Spatial Analyses — revised learning edition

This repository contains 91 browser-ready JupyterLite notebooks inspired by the Periodic Table of Geospatial Analysis: one index notebook plus 90 element notebooks.

## What changed

The notebooks were rebuilt around varied, compact teaching extracts from compelling open-data themes: Meuse heavy metals, SIDS-style county health rates, NYC taxi trips, Boston housing tracts, Iris measurements with synthetic coordinates, earthquakes, weather stations, bike-share trips, retail sites, and a raster-style landcover grid.

The notebooks are designed to run with the **Python (Pyodide)** kernel in JupyterLite. They avoid compiled GIS stacks such as GDAL, GeoPandas, Rasterio, Shapely, and PyProj. Instead they use transparent `pandas`, `numpy`, and `matplotlib` workflows plus a small local helper module, `spatial_lite.py`.

## Repository layout

- `notebooks/00_Index.ipynb` — table of all notebooks
- `notebooks/01_...` through `notebooks/90_...` — revised examples
- `data/*.csv` — local teaching datasets for offline/browser reliability
- `spatial_lite.py` — Pyodide-safe spatial helper functions
- `jupyter_lite_config.json` — content settings for a JupyterLite build

## Build locally

```bash
python -m pip install jupyterlite-core jupyterlite-pyodide-kernel
jupyter lite build --contents notebooks --contents data --contents spatial_lite.py
```

The build should publish notebooks and data into the JupyterLite site while keeping all examples browser-safe.
