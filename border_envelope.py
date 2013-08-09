from osgeo import ogr
from osgeo import osr
import os
import shutil

os.chdir("C:\Users\gramener\Desktop\sushmit\geospatial\shapefiles")

srcFile = ogr.Open("TM_WORLD_BORDERS\TM_WORLD_BORDERS-0.3.shp")

srclayer = srcFile.GetLayer(0)

if os.path.exists("bounding_boxes"):
	shutil.rmtree("bounding_boxes")
os.mkdir("bounding_boxes")

spatialReference = osr.SpatialReference()
spatialReference.SetWellKnownGeogCS('WGS84')

driver = ogr.GetDriverByName("ESRI Shapefile")
dstPath = os.path.join("bounding_boxes","boundingBoxes.shp")
dstFile = driver.CreateDataSource(dstPath)
dstLayer = dstFile.CreateLayer("Layer",spatialReference)

fieldDef = ogr.FieldDefn("COUNTRY",ogr.OFTString)
fieldDef.SetWidth(3)
dstLayer.CreateField(fieldDef)

fieldDef = ogr.FieldDefn("CODE", ogr.OFTString)
fieldDef.SetWidth(3)
dstLayer.CreateField(fieldDef)

countries = []

for i in range(srclayer.GetFeatureCount()):
	feature = srclayer.GetFeature(i)
	countryCode = feature.GetField("ISO3")
	countryName = feature.GetField("NAME")
	geometry = feature.GetGeometryRef()
	minLong,maxLong,minLat,maxLat = geometry.GetEnvelope()

	countries.append((countryName,countryCode,minLat,minLong,maxLat,maxLong))

	linearRing = ogr.Geometry(ogr.wkbLinearRing)
	linearRing.AddPoint(minLong, minLat)
	linearRing.AddPoint(maxLong, minLat)
	linearRing.AddPoint(maxLong, maxLat)
	linearRing.AddPoint(minLong, maxLat)
	linearRing.AddPoint(minLong, minLat)

	polygon = ogr.Geometry(ogr.wkbPolygon)
	polygon.AddGeometry(linearRing)

	feature = ogr.Feature(dstLayer.GetLayerDefn())
	feature.SetGeometry(polygon)
	feature.SetField("COUNTRY", countryName)
	feature.SetField("CODE", countryCode)
	dstLayer.CreateFeature(feature)
	feature.Destroy()

srcFile.Destroy()
dstFile.Destroy()

countries.sort()

for countryName,countryCode,minLat,minLong,maxLat,maxLong in countries:
	print "%s..(%s),Lat=(%.04f)..(%.04f),Long=(%.04f)..(%.04f)"%(countryName,countryCode,minLat,minLong,maxLat,maxLong)