import utils

if __name__=='__main__':

    print('processing temperature...')
    temperature = utils.get_dataframe_from_tiffs(years=[2012,], variable='Temperature')
    temperature.to_csv('processed_data/temperature.csv', index=False)
    del temperature
    print(f'temperature written to processed_data/temperature.csv')

    print('processing precipitation...')
    precipitation = utils.get_dataframe_from_tiffs(years=[2012,], variable='Precipitation')
    precipitation.to_csv('processed_data/precipitation.csv', index=False)
    del precipitation
    print('temperature written to processed_data/precipitation.csv')

    print('processing snow cover...')
    snowcover = utils.get_dataframe_from_tiffs(years=[2012,], variable='SnowCover', memory_issue=True)
    snowcover.to_csv('processed_data/snowcover.csv', index=False)
    del snowcover
    print('snow cover written to processed_data/snowcover.csv')

    print('Finished...')
