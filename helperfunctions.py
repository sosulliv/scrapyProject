#SPFileName="SPHistory.csv"
import pandas as pd
import numpy as np
import datetime
import dateutil.relativedelta
import statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests


def spDataCleansing(SPFileName):
    sandpData = pd.read_csv(SPFileName)
    sandpData=sandpData.drop([0,1116]) #Cleansing
    sandpData['Date']= pd.to_datetime(sandpData['Date'])
    sandpData=sandpData.rename(columns={"Adj Close**": "AdjClose", "Close*": "Close",}, errors="raise")
    sandpData['AdjCloseInt'] = sandpData['AdjClose'].replace({'\$': '', ',': ''}, regex=True).astype(float)

    sandpData=sandpData.sort_values(by=['Date'])
    sandpData['Date']= pd.to_datetime(sandpData['Date']).dt.date+dateutil.relativedelta.relativedelta(days=1)
    sandpData['Rate']= round(sandpData.AdjCloseInt.pct_change() * 100,1)
    sandpData['RateNeg']= round(sandpData.AdjCloseInt.pct_change() * 100,1)*-1
    sandpData['RRChange']= round(sandpData.Rate.pct_change() * 100,1)

    #sandpData['quarter'] = sandpData['Date'].dt.quarter
    #sandpData['year'] = sandpData['Date'].dt.year
    #sandpData["yearmo"] = sandpData["year"].astype(str) + "-" + sandpData["quarter"].astype(str) 

    sandpData["AdjCloselog"] = np.log(sandpData["AdjCloseInt"])

    sandpData=sandpData[sandpData['Date'] >= pd.to_datetime("1962-01-01").date() ] 
    sandpData=sandpData[sandpData['Date'] < pd.to_datetime("2020-11-01").date()]
    return sandpData

def dgs10DataCleansing(DG10FileName):
    treasuriesData = pd.read_csv(DG10FileName)
    treasuriesData['DATE']= pd.to_datetime(treasuriesData['DATE'])
    treasuriesData=treasuriesData.rename(columns={"DATE": "Date", "DGS10": "Rate"}, errors="raise")
    treasuriesData=treasuriesData.sort_values(by=['Date'])
    treasuriesData['Rate']= round(treasuriesData.Rate,1)
    treasuriesData['ChangeRate']= round(treasuriesData.Rate.pct_change() * 100,1)
    treasuriesData['ChangeRate'] = treasuriesData['ChangeRate'].fillna(0)

    treasuriesData['quarter'] = treasuriesData['Date'].dt.quarter
    treasuriesData['year'] = treasuriesData['Date'].dt.year
    treasuriesData["yearmo"] = treasuriesData["year"].astype(str) + "-" + treasuriesData["quarter"].astype(str) 

    treasuriesData["RateLog"] = np.log(treasuriesData["Rate"])
    treasuriesData['Date_2'] = pd.to_datetime(treasuriesData['Date']).dt.date
    treasuriesData['Date_3']=treasuriesData['Date_2'] - dateutil.relativedelta.relativedelta(months=1)

    treasuriesData['Date'] = pd.to_datetime(treasuriesData['Date']).dt.date
    treasuriesData=treasuriesData[treasuriesData['Date'] < pd.to_datetime("2020-11-01").date()]

    return treasuriesData

def consolidateDataSet(SPData,DGS10Data):
  
    df = SPData.set_index('Date')
    d = DGS10Data.set_index('Date')

    result=df.merge(d, on='Date', how='inner')
    #result3.reset_index(inplace=True)
    result = result[[ "AdjCloseInt", "Rate_y"]]
    #result.info()
    result=result.rename(columns={"AdjCloseInt":"SPClose",  "Rate_y": "InterestRate"})
    return result

def augmented_dickey_fuller_statistics(time_series):
    result = sm.tsa.stattools.adfuller(time_series.values)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))


maxlag=12

test = 'ssr-chi2test'

def grangers_causality_matrix(data, variables, test = 'ssr_chi2test', verbose=False):

    dataset = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)

    for c in dataset.columns:
        for r in dataset.index:
            test_result = grangercausalitytests(data[[r,c]], maxlag=maxlag, verbose=False)
            p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
            if verbose: print(f'Y = {r}, X = {c}, P Values = {p_values}')

            min_p_value = np.min(p_values)
            dataset.loc[r,c] = min_p_value

    dataset.columns = [var + '_x' for var in variables]

    dataset.index = [var + '_y' for var in variables]

    return dataset