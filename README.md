# CT Organ Reconstruction

Interactive 3D reconstruction of human organs from CT scan stacks —
segmenting bones, lungs, and soft tissue then rendering photorealistic
surface meshes using PyVista.

---

## What it does

Takes a stack of CT scan DICOM slices → segments organs by tissue density
→ applies Marching Cubes surface reconstruction → renders an interactive
3D mesh you can rotate, zoom, and explore in real time.

---

## Visual pipeline
```
CT DICOM stack → 3D volume → Segmentation → Marching Cubes → 3D mesh
     (2D slices)    (voxels)   (thresholding)  (surface)     (PyVista)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Medical image loading | SimpleITK, pydicom |
| Volume processing | NumPy, SciPy |
| Segmentation | Intensity thresholding + morphological operations |
| Surface reconstruction | Scikit-image (Marching Cubes) |
| 3D rendering | PyVista |
| Visualization | Matplotlib, PyVista |
| Dataset | TCIA / Medical Segmentation Decathlon |

---

## Project structure
```
ct-organ-reconstruction/
├── data/
│   └── (download instructions in docs/SPEC.md)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_segmentation.ipynb
│   ├── 03_3d_reconstruction.ipynb
│   └── 04_rendering.ipynb
├── src/
│   ├── loader.py
│   ├── segmentation.py
│   └── reconstruction.py
├── outputs/
│   └── (rendered images and meshes)
├── docs/
│   └── SPEC.md
└── README.md
```

---

## Progress log

- [x] Project defined and documented
- [ ] CT data loading and exploration
- [ ] Organ segmentation
- [ ] 3D surface reconstruction
- [ ] Interactive rendering and visualization
- [ ] Demo screenshots/GIF for README

---

## Author

**Hidayet Allah Yaakoubi**
BME student — Tunisia
```