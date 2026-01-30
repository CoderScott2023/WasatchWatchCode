!pip install rasterio

import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from google.colab import drive
from matplotlib.colors import LinearSegmentedColormap

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/InputFolder'
outputDir = '/content/drive/My Drive/OutputFolder'
os.makedirs(outputDir, exist_ok=True)


ee_palette = [
    '#d7191c',  # red
    '#fdae61',  # orange
    '#ffffbf',  # yellow
    '#a6d96a',  # light green
    '#1a9641'   # dark green
]

cmap = LinearSegmentedColormap.from_list("ndvi_gradient", ee_palette)

vmin, vmax = 0, 1

for filename in sorted(os.listdir(dataDir)):
    if not filename.endswith('.tif'):
        continue

    filePath = os.path.join(dataDir, filename)
    print("Processing:", filename)

    with rasterio.open(filePath) as src:
        ndviData = src.read(1)

    ndviData = np.nan_to_num(ndviData, nan=0)

    plt.figure(figsize=(10, 8))
    plt.imshow(ndviData, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label='NDVI Z-score (same scale as Earth Engine)')
    plt.title(f'NDVI Gradient Map (EE Style) - {filename}')
    plt.axis('off')

    out = os.path.join(outputDir, filename.replace('.tif', '.png'))
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()

print("Complete")
