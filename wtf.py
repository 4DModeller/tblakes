# !pip install folium
# !pip install geopandas
# !pip install rasterio
# !pip install geoviews
# !pip install xarray
# !pip install cdsapi
# !pip install regionmask
# !pip install rioxarray
# !pip install cftime
# !pip install earthengine-api --upgrade
# !pip install xgboost

# Import necessary libraries
import folium
import numpy as np
import rasterio
import rasterio.plot
# from rasterio.mask import mask
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
# from PIL import Image
import pandas as pd
# import regionmask

import xgboost

# Define locations
tibetan_plateau_location = (34.25, 88.75)
mount_everest_location = (27.9881, 86.9250)
k2_location = (35.8825, 76.5133)

# Define map
interactive_map = folium.Map(location=tibetan_plateau_location, zoom_start=6)

tile = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(interactive_map)

# Add markers
folium.Marker(location=mount_everest_location, popup=\Mount Everest\).add_to(interactive_map)
folium.Marker(location=k2_location, popup=\K2\).add_to(interactive_map)

# Add GeoJSON layer
# folium.GeoJson(
#     data=open(\tibetan_plateau.geojson\, \r\).read(),
#     name=\geojson\
# ).add_to(interactive_map)

# Show the map
interactive_map

# # we need to download covariate data, we will start with the ERA5-land precipitation data
# 
# Since it is likely that lakes are growing because it is raining, at least in part, we download ERA5-land data for 1984 until 2021. Then we plot it. This will be used as a covariate in the model.
# 
# If you do not have API access to CDS then you should go here first:
# 
# https://cds.climate.copernicus.eu/api-how-to

# this may take some time to run

downloaded = True

if downloaded == False:

    import cdsapi

    c = cdsapi.Client()

    years = np.arange(1984, 2022, 1)
    days = [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ]
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    times = '23:00'
    area = [45, 68, 24, 107]

    for year in years:
        year = str(year)
        c.retrieve('reanalysis-era5-land', {'year':year, 'month':months, 'time':times, 'day':days, 'area':area
                                           ,'variable':'total_precipitation', 'format':'netcdf.zip'}
                  ,'precip-'+year+'netcdf.zip')

# now we need to unzip the data
if downloaded == False:
    import glob
    import shutil
    for f in glob.glob('data/precip/*'):
        unzipped_filename = f.split('-')[1][0:4]
        shutil.unpack_archive(f, unzipped_filename)

# make map of ERA5-land precipitation data
import holoviews as hv
hv.extension('bokeh', 'holoviews')\n

import xarray as xr
import geoviews as gv
import geoviews.feature as gf
from geoviews import opts
from holoviews.operation.datashader import regrid

# Open the NetCDF dataset
dataset = xr.open_mfdataset('data/precip/1986/data.nc')

# Convert the xarray dataset to a holoviews dataset
hv_dataset = hv.Dataset(dataset)

# Create an image from the dataset and specify the kdims
image = hv_dataset.to(gv.Image, kdims=['longitude', 'latitude'])

# Regrid the image for better performance
regridded = regrid(image)

# Add a base map
base_map = gv.tile_sources.CartoLight.opts(width=600, height=400)

# Render the map with the regridded image and the base map
final_map = base_map * regridded

final_map.opts(
    opts.Image(cmap='nipy_spectral', colorbar=True, alpha=1),
    opts.Overlay(active_tools=['wheel_zoom'])
)

# We need to download the water location data which can be taken from the global water surface data set

We use google earth engine data product global water surface data set: https://global-surface-water.appspot.com/


# use GEE api to download data
import ee
ee.Authenticate()
ee.Initialize()
print(ee.Image(\NASA/NASADEM_HGT/001\).get(\title\).getInfo())

# Load an image.
import folium

def add_ee_layer(self, ee_image_object, vis_params, name):
    \\\
    folium doesn't include a built in function to add earth engine
    layers. This function fixes this issue.
    \\\
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
      tiles=map_id_dict['tile_fetcher'].url_format,
      attr='Map Data &copy; <a href=\https://earthengine.google.com/\>Google Earth Engine</a>',
      name=name,
      overlay=True,
      control=True
    ).add_to(self)

folium.Map.add_ee_layer = add_ee_layer

# image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_044034_20140318')

# # Define the visualization parameters.
# image_viz_params = {
#     'bands': ['B5', 'B4', 'B3'],
#     'min': 0,
#     'max': 0.5,
#     'gamma': [0.95, 1.1, 1]
# }

# # Define a map centered on San Francisco Bay.
# map_l8 = folium.Map(location=[37.5010, -122.1899], zoom_start=10)

# # Add the image layer to the map and display it.
# map_l8.add_ee_layer(image, image_viz_params, 'false color composite')
# display(map_l8)

# wawa = ee.ImageCollection('JRC/GSW1_4/YearlyHistory')
wawa = ee.Image('JRC/GSW1_0/GlobalSurfaceWater')

gsw_monthly = ee.ImageCollection('JRC/GSW1_4/MonthlyHistory')

gsw_monthly = ee.ImageCollection('JRC/GSW1_4/MonthlyHistory')

reducer = ee.Reducer.max()

yearlist = ee.List.sequence(1984, 2021) 

# // map over the list of years to generate a composite for each year.
# var yearCompList = yearlist.map(function(year){
  
#   var yearCol = gsw_monthly.filter(ee.Filter.calendarRange(year, year, 'year'))
#   var yearMax = yearCol.reduce(reducer);   // reducer
  
#   var imgList = yearCol.aggregate_array('system:index');
#   var n_img = imgList.size();
#   var nBands = yearMax.bandNames().size();
#   return yearMax.set({
#     'year': year,
#     'image_list': imgList,
#     'n_bands': nBands,
#     'n_img': n_img,
#     'method': 'max vallue',
#     'system:time_start': year
#   });
# });

def yearCompList(year):
    yearCol = gsw_monthly.filter(ee.Filter.calendarRange(year, year, 'year'))
    yearMax = yearCol.reduce(reducer)
    
    imgList = yearCol.aggregate_array('system:index')
    n_img = imgList.size()
    nBands = yearMax.bandNames().size()
    
    return yearMax.set({'year':year
                        ,'image_list':imgList
                        ,'n_bands':nBands
                        ,'n_img':n_img
                        ,'method':'max vallue'
                        ,'system:time_start':year
                       })

years = np.arange(1984, 2020, 1)
# yearCompList = [yearCompList(year) for year in years]


# // create collection: 
# // convert the annual composite image list to an ImageCollection and filter out years with no images.
anns_max = {}
for year in years:
    annual_max_water = ee.ImageCollection.fromImages(yearCompList(year)).filter(ee.Filter.gt('n_bands', 0))
    anns_max[year] = annual_max_water
# print('annual_max_water', annual_max_water)

annualList = anns_max.values()



# // function
# var difference = function(img){
  
#   // recode images to 0 and 1
#   img = img.updateMask(img.eq(2)).multiply(0).add(1).unmask(0)
  
#   // make first image *10: 
#   var img = img.multiply(10)//.copyProperties(img, [\year\])

#   // get index of the image
#   var index = annual_list.indexOf(img)
#   // index - 1 
#   var previousIndex = ee.Algorithms.If(index.eq(0), index, index.add(1))
  
#   // previous image
#   var previousImage = ee.Image(annual_list.get(previousIndex))
#   var previousImage = previousImage.updateMask(previousImage.eq(2)).multiply(0).add(1).unmask(0)

#   // calculate difference
#   var change = img.add(previousImage).copyProperties(previousImage, ['max vallue', 'n_img', 'system:time_start', 'year'])
  
#   return change;
# }


# // map function
# var newdiff = annual_max_water.map(difference)//.copyProperties(img, ['max vallue', 'n_img', 'system:time_start', 'year'])
# print('newdiff', newdiff)

# def difference(img):
#     img = img.updateMask(img.eq(2)).multiply(0).add(1).unmask(0)
#     img = img.multiply(10)
    
#     # index = annual_list.indexOf(img)
#     index = 
#     previousIndex = ee.Algorithms.If(index.eq(0), index, index.add(1))
    
#     # previousImage = ee.Image(annual_list.get(previousIndex))
#     previousImage = ee.Image(annual_list[previousIndex])


def difference(img1, img2):
    \\\
    img1 : image of lakes in year n
    img2 : image of lakes in year n - 1
    \\\
    img1 = ee.Image(img1)
    img2 = ee.Image(img2)
    
    img1 = img1.multiply(10)
    
    img2 = img2.updateMask(img2.eq(2)).multiply(0).add(1).unmask(0)
    
    diff = img1.add(img2).copyProperties(img2, ['max vallue', 'n_img', 'system:time_start', 'year'])
    
    return diff
# for year in years:
    
difference(anns_max[1999], anns_max[1998])


d = difference(anns_max[1999], anns_max[1998])

# ee.Image(d)

img1 = ee.Image(anns_max[1999])

maptest = folium.Map(location=tibetan_plateau_location)
vis_params = {'bands':'max vallue'}
maptest.add_ee_layer(img1, vis_params, 'whatever')


# Define a map centered on San Francisco Bay.
map_l8 = folium.Map(location=tibetan_plateau_location)

# Add the image layer to the map and display it.
# vis_params = {'bands':['occurrence',]}
# map_l8.add_ee_layer(wawa, vis_params, 'whatever')
vis_params = {'bands':['max vallue',]}
map_l8.add_ee_layer(difference(anns_max[1999], anns_max[1998]), vis_params, 'whatever')
display(map_l8)


# Catchment level modeling

In order to model the data, we will look at catchment level changes between lake positive/negative growth within catchments and their covariates (e.g., precipitation). We will use the hydrobasins catchment data: https://www.hydrosheds.org/products/hydrobasins

We use catchment level 6.


# Import necessary libraries
import folium
import geopandas as gpd
from shapely.geometry import Polygon

# Define initial location (Tibetan Plateau coordinates)
initial_location = (34.25, 88.75)

# Read the shapefile using geopandas
gdf = gpd.read_file('data/hydrobasins_lvl6/hybas_as_lev06_v1c.shp')

# Convert the shapefile data to json
gdf_json = gdf.to_json()

# Create a folium map object
m = folium.Map(location=initial_location, zoom_start=5)

# Add the shapefile data to the map
folium.GeoJson(
    gdf_json,
    name=\geojson\
).add_to(m)

# Display the map in the Jupyter Notebook
m\n


shapefile_path = 'data/hydrobasins_lvl6/hybas_as_lev06_v1c.shp'
shapes = gpd.read_file(shapefile_path)\n


netcdf_path = 'data/precip/1984/data.nc'
dataset = xr.open_dataset(netcdf_path)\n


def get_precip_data_for_year(data_path, shapes):
    dataset = xr.open_dataset(data_path)
    
    sums = []
    
    for index, shape in shapes.iterrows():
        # Extract the geometry
        geom = shape.geometry

        # Select the data from the NetCDF file using the geometry
        # because \nearest\ method is used, even if there is no data
        # , it will calculate an average for data nearest to it
        # this makes it appear like there is data for areas where there is none (e.g., in Japan).
        # TODO : needs to label whether a shape is part of tibetan plateau or not
        data = dataset.sel(longitude=geom.centroid.x, latitude=geom.centroid.y, method='nearest')
        # data = dataset.sel(longitude=geom.centroid.x, latitude=geom.centroid.y, method=None)

        # Calculate the sum of the data
        # data_sum = data.sum()
        data_sum = data.sum()['tp'].values

        # Append the sum to the list
        sums.append(data_sum)
        
    return sums


# precip_1984 = get_precip_data_for_year('data/precip/1984/data.nc', shapes=shapes)


years = np.arange(1984, 2022, 1)

final_data_set = pd.DataFrame()

for year in years:
    precip = get_precip_data_for_year(f'data/precip/{year}/data.nc', shapes=shapes)
    year_df = pd.DataFrame()
    year_df['precip'] = precip
    year_df['precip'] = year_df['precip'].astype(np.float64)
    year_df['year'] = year
    final_data_set = pd.concat([final_data_set, year_df])
    
final_data_set.head()


final_data_set.tail()


# Calculate the centroid of each shape and add a marker to the map
shapes['centroid_lon'] = shapes.apply(lambda row: row['geometry'].centroid.x, axis=1)
shapes['centroid_lat'] = shapes.apply(lambda row: row['geometry'].centroid.y, axis=1)


final_data_set = final_data_set.join(shapes).sort_values(by=['year', 'SORT'])
final_data_set = gpd.GeoDataFrame(final_data_set)

# bounding box from precip data
xmin = 45
xmax = 107
ymin = 24
ymax = 68

final_data_set = final_data_set.cx[xmin:xmax, ymin:ymax]


final_data_set.describe()


fig, ax = plt.subplots(figsize=(15, 15))
# # [45, 68, 24, 107]
# xmin = 45
# xmax = 107
# ymin = 24
# ymax = 68
cbar = final_data_set[final_data_set.year==2017].plot('precip', ax=ax, cmap='PRGn', vmax=1)
# fig.colorbar(cbar)


# Creating fake data

since there is no lake growth data yet i will create some fake data so it can go into 4d-modeller for testing

first i'll create a linear relationship where the more northeast it is, the more the lakes grow.

Then I will create a temporal relationship where the more recent it is, the more the lakes grow.


def get_random_lake_growth():
    growth = np.random.normal(loc=0, scale=2, size=1)
    # if growth < 0:
    #     growth = (0,)
    return growth[0]


final_data_set['spatial_growth'] = final_data_set.apply(lambda row: (row['centroid_lon']/xmax + row['centroid_lat']/ymax) * get_random_lake_growth(), axis=1)\n'
final_data_set['lake_growth'] = final_data_set.apply(lambda row: (row['year'] - 1984)/years.shape[0] * row['spatial_growth'], axis=1)\n


final_data_set[final_data_set.year==2017].plot('lake_growth', cmap='PRGn')


final_data_set.groupby('year').mean().lake_growth.plot()


# Now we combine everything into one data set for 4DM

Since the model is implemented in R we first will create the dataset for that model, then export it. Then, in a separate R-markdown file, we will do the modeling.

This process will be used as the basis to create all of the covariates used in the model.

We will also include data from the hydrobasins dataset, such as whether a catchment is connected or not


only_variables = final_data_set.copy()
only_variables = only_variables[['precip', 'year', 'ENDO', 'centroid_lon', 'centroid_lat', 'lake_growth']]
only_variables.to_csv('data_for_4dm.csv')