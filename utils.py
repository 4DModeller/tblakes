import rasterio
import numpy as np
import pandas as pd
import os
import tqdm


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

def process_geotiff_in_chunks(geotiff_path, chunk_size=1024):
    with rasterio.open(geotiff_path) as src:
        # Getting the dimensions of the image
        width = src.width
        height = src.height

        varname = geotiff_path.split('_')[0]

        n_chunks = ((width - 1) // chunk_size + 1) * ((height - 1) // chunk_size + 1)
        pbar = tqdm(total=n_chunks, desc='Processing GeoTIFF')

        df = pd.DataFrame()

        for i in range(0, width, chunk_size):
            for j in range(0, height, chunk_size):
                # Define the window
                window = rasterio.windows.Window(i, j, chunk_size, chunk_size)
                
                # Read the data in the defined window
                data = src.read(1, window=window)

                # Handle edge cases where the window might exceed the image dimensions
                if data.size == 0:
                    continue  # Skip empty windows

                # Process the chunk of data
                # For example, converting it to a DataFrame
                rows, cols = np.indices(data.shape)
                x_coords, y_coords = rasterio.transform.xy(src.transform, rows + j, cols + i, offset='center')
                x_coords = np.array(x_coords).flatten()
                y_coords = np.array(y_coords).flatten()
                pixel_values = data.flatten()

                df_chunk = pd.DataFrame({
                    'x_coord': x_coords,
                    'y_coord': y_coords,
                    # 'pixel_value': pixel_values
                    f'{varname}': pixel_values
                })

                # Append or process this chunk DataFrame as needed
                df = pd.concat([df, df_chunk])
            pbar.update(1)
        
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

def get_dataframe_from_tiffs(years, variable, memory_issue=False):
    """maps the geotiff_to_dataframe function to all the data files.

    Args:
        years (list): a list of years to iterate across
        variable (str): variable name

    Returns:
        pandas.DataFrame: pandas dataframe containing all of the data
    """
    if memory_issue==False:
            
        all_dfs = []
        for year in years:
            yeardf = pd.concat(
                list(map(geotiff_to_dataframe, get_filenames_with_string('EarthEngineData/', variable+'_'+str(year)))))
            yeardf['year'] = year
            all_dfs.append(yeardf)
            
        return pd.concat(all_dfs)

    else:
        # # TODO : implement
        all_dfs = []
        for year in years:
            year_df = pd.concat(list(map(process_geotiff_in_chunks, get_filenames_with_string('EarthEngineData/', variable+'_'+str(year)))))
            year_df['year'] = year
            all_dfs.append(year_df)
        
        return pd.concat(all_dfs)

if __name__=='__main__':
    print('One day this might be implemented as a CLI but not this day.')