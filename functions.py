import pandas as pd
import numpy as np
import json
import time
from google_currency import convert 

def extract_data():
    #upload the world bank data
    twb_data = pd.read_csv('/Users/mikel/Documents/Projects/chameleon-pricing/twb_data.csv', sep=",", skiprows=3)
    twb_data=twb_data.drop(columns=['Unnamed: 65', 'Indicator Name', 'Indicator Code'])
    twb_data=twb_data.dropna(axis=1,how='all')
    #get last ppp value and create a new column
    twb_data['last_value'] = twb_data.ffill(axis=1).iloc[:, -1] 
    #delete rows with all null values in numeric columns
    twb_data=twb_data[pd.to_numeric(twb_data['last_value'], errors='coerce').notnull()]
    #create a new dataframe with this 2 columns
    df1=twb_data[['Country Name', 'last_value']]
    df1=df1.rename(columns={'Country Name' : 'Country'})
    #get currency codes
    currency=pd.read_html('https://docs.1010data.com/1010dataReferenceManual/DataTypesAndFormats/currencyUnitCodes.html')
    currency=currency[0]
    currency['Entity']=currency['Entity'].str.lower()
    df1['Country']=df1['Country'].str.lower()
    currency.Entity=currency.Entity.replace('bolivia, plurinational state of', 'bolivia')
    currency.Entity=currency.Entity.replace('venezuela, bolivarian republic of', 'venezuela, rb')
    #merge dataframes
    country_currency=df1.merge(currency, left_on='Country', right_on='Entity')
    country_currency=country_currency[['Country', 'last_value', 'Currency', 'Code']]
    #save to csv country_currency
    country_currency.to_csv('/Users/mikel/Documents/Projects/chameleon-pricing/country_currency.csv', index=False)

def transform_data():
    #read previous csv
    df=pd.read_csv('/Users/mikel/Documents/Projects/chameleon-pricing/country_currency.csv')
    #change ppp values to the same currency, dollar
    def ppp_to_dollar(Code, last_value):
        conversion=convert(Code, 'usd', last_value)
        result = json.loads(conversion)
        return result['amount']
    apply = df.apply(lambda x: ppp_to_dollar(x['Code'], x['last_value']),axis=1)
    df['ppp_todollar']  = apply
    df["ppp_todollar"] = df.ppp_todollar.astype(float)
    #adapt previous value to spain
    adjustment=1/(df.ppp_todollar[df.Country == 'spain'])
    def ppp_to_spain(ppp_to_dollar):
        return round(ppp_to_dollar*adjustment, 2)
    apply = df.apply(lambda x: ppp_to_spain(x['ppp_todollar']), axis=1)
    df['ppp_spain']  = apply
    df["ppp_spain"] = df.ppp_spain.astype(float)
    #fix Germany
    df.ppp_todollar[df.Country == 'germany']=ppp_to_dollar('EUR', 0.733679)
    df.ppp_spain[df.Country == 'germany']=ppp_to_spain(0.87)
    #drop null columns
    df.drop(df[df['ppp_todollar'] == 0.0].index, inplace = True)
    #save to excel DB
    df.to_excel('/Users/mikel/Documents/Projects/chameleon-pricing/DB.xlsx', index=False)

    