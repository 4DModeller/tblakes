import rasterio
import numpy as np
import pandas as pd

def geotiff_to_dataframe(geotiff_path):
    """
    Converts a geotiff to a pandas dataframe
    
    """
    with rasterio.open(geotiff_path) as src:
        data = src.read(1)  # Reading the first band
        nodata = src.nodata

        # Extracting coordinates and values
        pixel_values = data.flatten()
        rows, cols = np.indices(data.shape)
        x_coords, y_coords = rasterio.transform.xy(src.transform, rows, cols, offset='center')
        x_coords = np.array(x_coords).flatten()
        y_coords = np.array(y_coords).flatten()
        
        varname = geotiff_path.split('_')[0]

        # Creating DataFrame
        df = pd.DataFrame({
            'x_coord': x_coords,
            'y_coord': y_coords,
            f'{varname}':pixel_values
        })
        df = df[df[f'{varname}'] != nodata]  # Removing NoData values
        return df

def get_filenames_with_string(directory_path, search_string):
    matching_filenames = []
    for filename in os.listdir(directory_path):
        if search_string in filename:
            matching_filenames.append(filename)
    return [directory_path + fn for fn in matching_filenames]

def get_dataframe_from_tiffs(years, variable):
    all_dfs = []
    for year in years:
        yeardf = pd.concat(list(map(geotiff_to_dataframe, get_filenames_with_string('EarthEngineData/', variable+'_'+str(year)))))
        yeardf['year'] = year
        all_dfs.append(yeardf)
        
    return pd.concat(all_dfs)