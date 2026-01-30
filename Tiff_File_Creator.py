import ee
import datetime

ee.Authenticate()
ee.Initialize(project="Your Google Cloud Console Project ID Here")

wasatchFrontAreaBounding = ee.Geometry.Polygon([[
    [-113, 40], [-113, 42],
    [-111, 42], [-111, 40],
    [-113, 40]
]])
region_coords = wasatchFrontAreaBounding.getInfo()["coordinates"]

landsat_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA") \
    .filterDate("2013-03-01", "2026-01-01") \
    .filterBounds(wasatchFrontAreaBounding)

def getMedianImageOfMonth(year, month):
    start = datetime.date(year, month, 1)
    end = datetime.date(year + (month == 12), (month % 12) + 1, 1)
    img = landsat_8.filterDate(str(start), str(end)).median()
    if img.bandNames().size().getInfo() == 0:
        return None
    return img

def createNDVImap(year, month):
    monthlyMedian = getMedianImageOfMonth(year, month)
    if monthlyMedian is None:
        return None
    ndvi = monthlyMedian.normalizedDifference(["B5", "B4"]).rename("NDVI")
    if ndvi.bandNames().size().getInfo() == 0:
        return None
    return ndvi


gradient_palette = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

year = 2024
month = 12

ndvi = createNDVImap(year, month)
if ndvi is None:
    print("SKIPPED (no data) export for selected month")
else:
    ndvi_min = ndvi.reduceRegion(
        reducer=ee.Reducer.min(),
        geometry=wasatchFrontAreaBounding,
        scale=30,
        maxPixels=1e13
    ).get("NDVI")
    
    ndvi_max = ndvi.reduceRegion(
        reducer=ee.Reducer.max(),
        geometry=wasatchFrontAreaBounding,
        scale=30,
        maxPixels=1e13
    ).get("NDVI")
    
    minmax = ndvi.subtract(ee.Number(ndvi_min)).divide(
        ee.Number(ndvi_max).subtract(ee.Number(ndvi_min))
    ).rename("NDVI_MinMax")

    vis_params = {
        'min': 0,
        'max': 1,
        'palette': gradient_palette
    }

    task = ee.batch.Export.image.toDrive(
        image=minmax.clip(wasatchFrontAreaBounding),
        description="NDVI_MinMax_"+str(year)+"_"+str(month),
        folder="",
        scale=5550,
        region=region_coords,
        maxPixels=1e13,
        fileFormat='GeoTIFF'
    )
    task.start()
print("Complete")
