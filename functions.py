def extract_data():
    #read data and drop nulls
    twb_data = pd.read_csv('/Users/mikel/Documents/Projects/chameleon-pricing/twb_data.csv', sep=",", skiprows=3)
    twb_data=twb_data.drop(columns=['Unnamed: 65', 'Indicator Name', 'Indicator Code'])
    twb_data=twb_data.dropna(axis=1,how='all')
    #get last ppp_value
    twb_data['last_value'] = twb_data.ffill(axis=1).iloc[:, -1] 
    twb_data=twb_data[pd.to_numeric(twb_data['last_value'], errors='coerce').notnull()]
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
    #save to csv
    country_currency.to_csv('/Users/mikel/Documents/Projects/chameleon-pricing/country_currency.csv', index=False)

def transform_data():
    df=pd.read_csv('/Users/mikel/Documents/Projects/chameleon-pricing/country_currency.csv')
    #function, adapt ppp to dollar
    def ppp_to_dollar(Code, last_value):
        # cambiar a dollares y aplicar ppp
        conversion=convert(Code, 'usd', last_value)
        result = json.loads(conversion)
        # la salida en euros
        return result['amount']
    #function, adapt ppp to spain
    def ppp_to_spain(ppp_to_dollar):
        return round(ppp_to_dollar*1.315, 2)
    #get conversions and add to a column
    apply = df.apply(
         lambda x: ppp_to_dollar(x['Code'], x['last_value']),
         axis=1)
    df['ppp_todollar']  = apply
    #get adapted ppp for spain and add to a column
    apply = df.apply(
        lambda x: ppp_to_spain(x['ppp_todollar']),
        axis=1)
    df['ppp_spain']  = apply
    df["ppp_todollar"] = df.ppp_todollar.astype(float)
    #drop not converted ones
    df.drop(df[df['ppp_todollar'] == 0.0].index, inplace = True)
    #save to excel
    df.to_excel('/Users/mikel/Documents/Projects/chameleon-pricing/DB.xlsx', index=False)

def get_eur():
    conversion=convert('usd', 'eur', 1)
    result = json.loads(conversion)
    usd_eur.eur[0] = result['amount']
    