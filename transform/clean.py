import pandas as pd
from .aux import existingYearDirectories

def readMergeClean(country, year):
    route ='./data/'+ country + '/' + str(year)

    try:
        productsRoute = route + '/products.csv'
        partnersRoute = route + '/partners.csv'
        exportValuesRoute = route + '/exportValues.csv'

        productsDf = pd.read_csv(productsRoute, names=['productId', 'product_code', 'product'])
        partnersDf = pd.read_csv(partnersRoute, names=['partnerId', 'partner_code', 'partner'])
        exportValuesDf = pd.read_csv(exportValuesRoute, names=['partnerId', 'productId', 'value'])
    
        complete = exportValuesDf.merge(partnersDf, how='left', on='partnerId')
        complete = complete.merge(productsDf, how='left', on='productId')
        complete['reporter'] = country
        complete['year'] = year
        complete = complete.drop(columns=['partnerId', 'productId'])
        return complete

    except FileNotFoundError:
        print("ERROR! The directory {} doesn't exists".format(route))


def selectRelevantData(data, year=None):
    
    products = ['06-15_Vegetable', '50-63_TextCloth', 
    '01-05_Animal','41-43_HidesSkin',  
    '25-26_Minerals', '68-71_StoneGlas', '16-24_FoodProd', '28-38_Chemicals',
    '44-49_Wood', '27-27_Fuels', 'UNCTAD-SoP4', '39-40_PlastiRub', '64-67_Footwear',
    '72-83_Metals', '84-85_MachElec', '86-89_Transport']
    
    regions = ['East Asia & Pacific', 'East Asia and Pacific', 'Europe & Central Asia', 'Europe and Central Asia', 'Middle East and North Africa',
        'Middle East & North Africa', 'World', 'Latin America & Caribbean', 'Latin America and Caribbean', 'Sub-Saharan Africa',
       'British Indian Ocean Ter', 'Us Msc.Pac.I', 'North America', 'South Asia']

    mask_products = data['product_code'].isin(products)
    mask_regions_partners = ~data['partner'].isin(regions)
    mask_regions_reporters = ~data['reporter'].isin(regions)
    reduceData = data[mask_products & mask_regions_partners & mask_regions_reporters ]

    return reduceData


def totalDataPerCountry(country):
    yearDataFrames = []
    for year in existingYearDirectories(country):
        yearDataFrames.append(readMergeClean(country, year))
    
    return pd.concat(yearDataFrames)


def totalData(countries):
    data = []
    for country in countries:
        try:
            data.append(totalDataPerCountry(country['name']))
        except ValueError:
            print('{} no exists.'.format(country))
            continue

    dataFrame = pd.concat(data)
     
    return selectRelevantData(dataFrame)


def filterYears(data, year=None):
    if year:
        year = str(year)
        mask_year = data['year'] == year
        reducedData= data[mask_year]
        return reducedData.groupby(['reporter', 'partner', 'year'])['value'].sum()

    return data.groupby(['reporter', 'partner', 'year'])['value'].sum()

def filterTop(data, year=None):
    
    return filterYears(data,year).groupby(level=["reporter"]).nlargest(5).reset_index(level=0, drop=True).reset_index()

def relevantPartners(data, year=None, tresshold=0.9):

    data = filterYears(data, year)
    df = []
    countries = data.reset_index()['reporter'].unique()
    for country in countries:
        temp = data.loc[country].sort_values(ascending=False)
        perc = temp/temp.sum()
        
        acum = 0 
        count = 0
        for row in perc:
            if acum < tresshold:
                acum = acum + row
                count += 1
            else:
                break
        
        
        temp = temp.to_frame().reset_index()
        temp['reporter'] = country
        df.append(temp[0:count])
        
    
    return pd.concat(df)

def saveRequestedData(data):
    try:
        data.to_csv("./finalData.csv", index=False)
        return print("Final Data save succesfully.")
    except:
        return print("Error loading the data.")

    



