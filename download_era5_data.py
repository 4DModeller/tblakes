
import cdsapi
import numpy as np

c = cdsapi.Client()

# years = np.arange(2000, 2022, 1)
years = np.arange(2000, 2012, 1)
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
    # year = str(year)

    # temperature data
    # c.retrieve('reanalysis-era5-land', {'year':year, 'month':months, 'time':times, 'day':days, 'area':area
    #                                    ,'variable':'2m_temperature', 'format':'netcdf.zip'}
    #           ,'data/temp/temp-'+year+'netcdf.zip')

    # glacier data
    c.retrieve(
        'derived-gridded-glacier-mass-change',
        {
            'variable': 'glacier_mass_change',
            'product_version': 'wgms_fog_2022_09',
            'format': 'zip',
            'hydrological_year': [
                # '2016_17', '2020_21',
                # f'{year}_{year - 2000 + 1}',
                # '2000_01',
                f'{year}_0{year - 2000 + 1}' if year - 2000 < 9 else f'{year}_{year - 2000 + 1}'
            ],
        },
        f'data/glacier/{year}glaciers.zip')
