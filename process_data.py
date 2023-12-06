import utils
# from tqdm import tqdm
import pandas as pd

def process_var(var, years):
    print(f'processing {var}...')
    return utils.get_dataframe_from_tiffs(years=years, variable=var)

def process_outcome(var, years):
    print(f'processing {var}...')
    return utils.get_dataframe_from_tiffs(years=years, variable=var)

if __name__=='__main__':

    years = [2012,]
    variables = ['Temperature', 'Precipitation']
    outcome_variables = ['Difference',]
    # mem_variables = ['snowcover',]
    mem_variables = list()
    # total_steps = 2 * (len(variables) + len(mem_variables) + len(outcome_variables))
    # pbar = tqdm(total=total_steps, desc='Process Data')

    processed_vars = {}
    for var in variables:
        processed_vars[var] = process_var(var=var, years=years)
        # pbar.update(1)

    for var in outcome_variables:
        processed_vars[var] = process_outcome(var=var, years=years)
        # pbar.update(1)

    df = pd.DataFrame()
    for var in processed_vars.keys():
        print(var)
        if df.empty == True:
            print(var)
            df = pd.concat([df, processed_vars[var]])
        else:
            df = df.join(processed_vars[var], on=['x_coord', 'y_coord', 'year'])
        # pbar.update(1)

    # print('processing temperature...')
    # temperature = utils.get_dataframe_from_tiffs(years=[2012,], variable='Temperature')
    # temperature.to_csv('processed_data/temperature.csv', index=False)
    # del temperature
    # print(f'temperature written to processed_data/temperature.csv')

    # print('processing precipitation...')
    # precipitation = utils.get_dataframe_from_tiffs(years=[2012,], variable='Precipitation')
    # precipitation.to_csv('processed_data/precipitation.csv', index=False)
    # del precipitation
    # print('temperature written to processed_data/precipitation.csv')

    # print('processing snow cover...')
    # snowcover = utils.get_dataframe_from_tiffs(years=[2012,], variable='SnowCover', memory_issue=True)
    # snowcover.to_csv('processed_data/snowcover.csv', index=False)
    # del snowcover
    # print('snow cover written to processed_data/snowcover.csv')

    print('Finished...')
