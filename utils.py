import rasterio
import numpy as np
import pandas as pd

def geotiff_to_dataframe(geotiff_path):
    """converts geotiff file to a pandas dataframe

    Args:
        geotiff_path (str): location of geotiff

    Returns:
        pandas.DataFrame: Dataframe with columns x_coord, y_coord, and the variable name which is inferred from the path
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
    """get file names in the directory that match the search string

    Args:
        directory_path (str): directory data is stored in
        search_string (str) : variable name to find in the file name

    Returns:
        list: list of the directory and file names
    """
    matching_filenames = []
    for filename in os.listdir(directory_path):
        if search_string in filename:
            matching_filenames.append(filename)
    return [directory_path + fn for fn in matching_filenames]

def get_dataframe_from_tiffs(years, variable):
    """maps the geotiff_to_dataframe function to all the data files.

    Args:
        years (list): a list of years to iterate across
        variable (str): variable name

    Returns:
        pandas.DataFrame: pandas dataframe containing all of the data
    """
    all_dfs = []
    for year in years:
        yeardf = pd.concat(list(map(geotiff_to_dataframe, get_filenames_with_string('EarthEngineData/', variable+'_'+str(year)))))
        yeardf['year'] = year
        all_dfs.append(yeardf)
        
    return pd.concat(all_dfs)

if __name__=='__main__':
    print('One day this might be implemented as a CLI but not this day.')