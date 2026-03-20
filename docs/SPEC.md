# Project Specification — CT Organ Reconstruction

**Author:** Hidayet Allah Yaakoubi
**Date:** March 2026
**Status:** In progress

---

## 1. Project summary

A 3D organ reconstruction pipeline that takes a stack of CT scan DICOM
slices, segments organs by tissue density using intensity thresholding
and morphological operations, reconstructs 3D surface meshes using the
Marching Cubes algorithm, and renders interactive photorealistic
visualizations using PyVista.

---

## 2. CT imaging background

A CT (Computed Tomography) scan measures X-ray attenuation at each point
in a 3D volume. Values are stored in Hounsfield Units (HU):

| Tissue | HU Range |
|---|---|
| Air | -1000 HU |
| Lung | -600 to -400 HU |
| Fat | -100 to -50 HU |
| Soft tissue | 20 to 80 HU |
| Liver | 40 to 70 HU |
| Blood | 30 to 45 HU |
| Bone | 400 to 1000 HU |

This density information enables tissue-specific segmentation using
simple thresholding — no machine learning required for bones and lungs.

---

## 3. Pipeline stages

### Stage 1 — Data loading
- Load DICOM series using SimpleITK
- Stack slices into 3D NumPy array
- Apply correct voxel spacing for accurate geometry

### Stage 2 — Preprocessing
- Clip HU values to relevant range (-1000 to 1000)
- Apply Gaussian smoothing to reduce noise
- Normalize to 0-1 range

### Stage 3 — Segmentation
- Bone: threshold HU > 400
- Lung: threshold HU between -600 and -400
- Soft tissue: threshold HU between 20 and 80
- Morphological operations to clean up masks

### Stage 4 — Surface reconstruction
- Apply Marching Cubes algorithm per organ mask
- Generate triangular surface mesh
- Smooth mesh with Laplacian smoothing

### Stage 5 — Rendering
- Load mesh into PyVista
- Apply organ-specific colors and opacity
- Render interactive 3D scene
- Export screenshots and GIF for README

---

## 4. Dataset

**Source:** Medical Segmentation Decathlon
**Task:** Task03_Liver (liver + tumor CT)
**URL:** medicaldecathlon.com
**Format:** NIfTI (.nii.gz)
**Size:** ~15GB full dataset, ~500MB single case

Alternative: TCIA (The Cancer Imaging Archive)
URL: cancerimagingarchive.net

---

## 5. Tools and technologies

- **SimpleITK** — medical image loading and resampling
- **pydicom** — DICOM file parsing
- **NumPy / SciPy** — volume processing and morphological operations
- **scikit-image** — Marching Cubes surface reconstruction
- **PyVista** — 3D mesh rendering and visualization
- **Matplotlib** — 2D slice visualization

---

## 6. Expected outputs

- Interactive 3D mesh viewer (PyVista window)
- High-resolution screenshots of reconstructed organs
- Animated GIF showing 360-degree rotation
- Exported STL mesh files
- Jupyter notebooks documenting every pipeline stage
```