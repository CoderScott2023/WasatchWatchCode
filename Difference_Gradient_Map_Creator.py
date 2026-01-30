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

file1 = 'PREVIOUS MONTH'
file2 = 'CURRENT MONTH TO ANALYZE DIFFERENCE'
filePath1 = os.path.join(dataDir, file1)
filePath2 = os.path.join(dataDir, file2)

print(f"Processing difference: {file1} - {file2}")

with rasterio.open(filePath1) as src1, rasterio.open(filePath2) as src2:
    data1 = src1.read(1)
    data2 = src2.read(1)

data1 = np.nan_to_num(data1, nan=0)
data2 = np.nan_to_num(data2, nan=0)

diff = data1 - data2

abs_max = np.max(np.abs(diff))
vmin, vmax = -abs_max, abs_max

plt.figure(figsize=(10, 8))
plt.imshow(diff, cmap=cmap, vmin=vmin, vmax=vmax)
plt.colorbar(label='NDVI Difference (file1 - file2)')
plt.title(f'NDVI Difference Map: {file1} - {file2}')
plt.axis('off')

out = os.path.join(outputDir, f"diff_{file1.replace('.tif','')}_{file2.replace('.tif','')}.png")
plt.savefig(out, dpi=300, bbox_inches='tight')
plt.close()

print("Done")
