"""
CT Organ Reconstruction Pipeline
Run this script to generate all outputs in one command:
    python run.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import measure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
import struct
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('outputs', exist_ok=True)
os.makedirs('outputs/meshes', exist_ok=True)

print("=" * 55)
print("  CT Organ Reconstruction Pipeline")
print("=" * 55)

# ── STEP 1 — Generate CT volume ────────────────────────────────────
print("\n[1/5] Generating CT volume...")

np.random.seed(42)

def generate_ct_volume(shape=(128, 256, 256)):
    volume = np.full(shape, -1000, dtype=np.float32)
    z, y, x = np.ogrid[:shape[0], :shape[1], :shape[2]]
    cz, cy, cx = shape[0]//2, shape[1]//2, shape[2]//2
    body = ((z-cz)/50)**2 + ((y-cy)/90)**2 + ((x-cx)/70)**2 < 1
    volume[body] = 50
    spine = ((y-cy)/8)**2 + ((x-cx)/8)**2 < 1
    volume[spine & body] = 700
    for i, zpos in enumerate(range(30, 100, 10)):
        angle = i * 0.3
        for t in np.linspace(0, np.pi, 60):
            rx = int(cx + 55 * np.cos(t) * np.cos(angle))
            ry = int(cy + 55 * np.sin(t))
            rz = int(zpos + 5 * np.sin(t * 2))
            if 0<=rx<shape[2] and 0<=ry<shape[1] and 0<=rz<shape[0]:
                volume[max(0,rz-2):rz+2,
                       max(0,ry-2):ry+2,
                       max(0,rx-2):rx+2] = 700
    lung_l = ((z-cz)/40)**2+((y-(cy-20))/35)**2+((x-(cx-25))/25)**2 < 1
    lung_r = ((z-cz)/40)**2+((y-(cy-20))/35)**2+((x-(cx+25))/25)**2 < 1
    volume[lung_l & body] = -500
    volume[lung_r & body] = -500
    liver = ((z-(cz+15))/25)**2+((y-(cy+15))/30)**2+((x-(cx+20))/28)**2 < 1
    volume[liver & body] = 60
    kidney_l = ((z-cz)/15)**2+((y-(cy+10))/12)**2+((x-(cx-30))/10)**2 < 1
    kidney_r = ((z-cz)/15)**2+((y-(cy+10))/12)**2+((x-(cx+30))/10)**2 < 1
    volume[kidney_l & body] = 30
    volume[kidney_r & body] = 30
    aorta = ((y-(cy+5))/6)**2 + ((x-(cx-8))/6)**2 < 1
    volume[aorta & body] = 40
    noise = np.random.normal(0, 15, shape).astype(np.float32)
    volume += noise
    volume = ndimage.gaussian_filter(volume, sigma=0.8)
    return volume

volume = generate_ct_volume()
print(f"    Volume shape: {volume.shape} — "
      f"HU range: {volume.min():.0f} to {volume.max():.0f}")

# ── STEP 2 — Segment organs ────────────────────────────────────────
print("\n[2/5] Segmenting organs...")

def segment_organs(volume):
    masks = {}
    bone = volume > 350
    bone = ndimage.binary_closing(bone, iterations=2)
    masks['bone'] = ndimage.binary_fill_holes(bone)

    lung = (volume > -700) & (volume < -300)
    labeled, n = ndimage.label(lung)
    sizes = ndimage.sum(lung, labeled, range(1, n+1))
    lung = np.isin(labeled, [i+1 for i,s in enumerate(sizes) if s>500])
    lung = ndimage.binary_closing(lung, iterations=3)
    masks['lungs'] = ndimage.binary_fill_holes(lung)

    liver = (volume > 45) & (volume < 80)
    liver = ndimage.binary_opening(liver, iterations=2)
    liver = ndimage.binary_closing(liver, iterations=4)
    liver = ndimage.binary_fill_holes(liver)
    labeled, n = ndimage.label(liver)
    if n > 0:
        sizes = ndimage.sum(liver, labeled, range(1, n+1))
        liver = labeled == (np.argmax(sizes) + 1)
    masks['liver'] = liver

    kidney = (volume > 20) & (volume < 45)
    kidney = ndimage.binary_opening(kidney, iterations=2)
    kidney = ndimage.binary_closing(kidney, iterations=3)
    labeled, n = ndimage.label(kidney)
    if n > 0:
        sizes = ndimage.sum(kidney, labeled, range(1, n+1))
        kidney = np.isin(labeled, np.argsort(sizes)[-2:]+1)
    masks['kidneys'] = kidney
    return masks

masks = segment_organs(volume)
for name, mask in masks.items():
    print(f"    {name:<10}: {mask.sum():>8,} voxels")

# ── STEP 3 — Build 3D meshes ───────────────────────────────────────
print("\n[3/5] Building 3D meshes (Marching Cubes)...")

organ_config = {
    'bone':    {'step':1, 'color':'#FFFFF0', 'alpha':0.85},
    'lungs':   {'step':2, 'color':'#4A90D9', 'alpha':0.55},
    'liver':   {'step':2, 'color':'#CC3333', 'alpha':0.75},
    'kidneys': {'step':1, 'color':'#E07820', 'alpha':0.85},
}

meshes = {}
for organ, config in organ_config.items():
    smoothed = ndimage.gaussian_filter(masks[organ].astype(float),
                                       sigma=1.5)
    verts, faces, normals, _ = measure.marching_cubes(
        smoothed, level=0.5, step_size=config['step'])
    meshes[organ] = {'verts':verts, 'faces':faces,
                     'color':config['color'], 'alpha':config['alpha']}
    print(f"    {organ:<10}: {len(verts):>6,} vertices, "
          f"{len(faces):>7,} faces")

# ── STEP 4 — Save outputs ──────────────────────────────────────────
print("\n[4/5] Saving outputs...")

# STL export
def save_stl(verts, faces, filename):
    with open(filename, 'wb') as f:
        f.write(b'\x00' * 80)
        f.write(struct.pack('<I', len(faces)))
        for face in faces:
            v0,v1,v2 = verts[face[0]],verts[face[1]],verts[face[2]]
            e1, e2 = v1-v0, v2-v0
            normal = np.cross(e1, e2)
            norm = np.linalg.norm(normal)
            if norm > 0: normal = normal/norm
            f.write(struct.pack('<fff', *normal))
            f.write(struct.pack('<fff', *v0))
            f.write(struct.pack('<fff', *v1))
            f.write(struct.pack('<fff', *v2))
            f.write(struct.pack('<H', 0))

for organ, mesh in meshes.items():
    path = f'outputs/meshes/{organ}.stl'
    save_stl(mesh['verts'], mesh['faces'], path)
    size = os.path.getsize(path)/1024**2
    print(f"    outputs/meshes/{organ}.stl — {size:.1f} MB")

all_verts = np.vstack([m['verts'] for m in meshes.values()])

# single render
fig = plt.figure(figsize=(10, 10), facecolor='#0a0a0a')
ax = fig.add_subplot(111, projection='3d', facecolor='#0a0a0a')
for organ, mesh in meshes.items():
    col = Poly3DCollection(mesh['verts'][mesh['faces']],
                           alpha=mesh['alpha'], linewidth=0)
    col.set_facecolor(mesh['color'])
    col.set_edgecolor('none')
    ax.add_collection3d(col)
ax.set_xlim(all_verts[:,0].min(), all_verts[:,0].max())
ax.set_ylim(all_verts[:,1].min(), all_verts[:,1].max())
ax.set_zlim(all_verts[:,2].min(), all_verts[:,2].max())
ax.view_init(elev=25, azim=45)
ax.set_axis_off()
ax.set_title('3D CT Organ Reconstruction',
             color='white', fontsize=16, pad=20)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=m['color'],
          label=o.capitalize()) for o,m in meshes.items()],
          loc='upper left', labelcolor='white',
          facecolor='#1a1a1a', edgecolor='#444', fontsize=12)
plt.savefig('outputs/3d_reconstruction.png', dpi=150,
            bbox_inches='tight', facecolor='#0a0a0a')
plt.close()
print("    outputs/3d_reconstruction.png")

# rotating GIF
print("\n[5/5] Generating rotation GIF (36 frames)...")
fig = plt.figure(figsize=(8, 8), facecolor='#0a0a0a')
ax = fig.add_subplot(111, projection='3d', facecolor='#0a0a0a')

def init():
    ax.cla()
    ax.set_facecolor('#0a0a0a')
    for organ, mesh in meshes.items():
        col = Poly3DCollection(mesh['verts'][mesh['faces']],
                               alpha=mesh['alpha'], linewidth=0)
        col.set_facecolor(mesh['color'])
        col.set_edgecolor('none')
        ax.add_collection3d(col)
    ax.set_xlim(all_verts[:,0].min(), all_verts[:,0].max())
    ax.set_ylim(all_verts[:,1].min(), all_verts[:,1].max())
    ax.set_zlim(all_verts[:,2].min(), all_verts[:,2].max())
    ax.set_axis_off()
    return []

def animate(frame):
    ax.view_init(elev=25, azim=frame*10)
    ax.set_title('3D CT Organ Reconstruction',
                 color='white', fontsize=14, pad=15)
    return []

ani = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=36, interval=100, blit=False)
ani.save('outputs/rotation.gif', writer='pillow', fps=10, dpi=80)
plt.close()
print("    outputs/rotation.gif")

print("\n" + "=" * 55)
print("  Done! All outputs saved to outputs/")
print("=" * 55)
print("\n  outputs/")
print("  ├── 3d_reconstruction.png")
print("  ├── rotation.gif")
print("  └── meshes/")
for organ in meshes.keys():
    print(f"      ├── {organ}.stl")