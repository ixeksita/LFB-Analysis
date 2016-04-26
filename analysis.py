# -*- coding: utf-8 -*-
#Exploratory analysis for LFB data
#This code is intended to provide an overview of the data contained in LFBincidents.csv
#corresponding to the fires registered between 2012 and 2015
#for more information on the dataset visit: www.london-fire.gov.uk

#Loading modules 
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Rectangle
import numpy as np

#reading the data from the csv and parsing the dates
dateparse = (lambda x: pd.to_datetime(x, format='%d-%b-%y'))
fire=pd.read_csv('LFB.csv', parse_dates=['DateOfCall'], 
               date_parser=dateparse)

#obtain the years from the date of call 
fire['Year'] = fire['DateOfCall'].map(lambda x: x.year)
fire['Month'] = fire['DateOfCall'].map(lambda x: x.month)

#set parameters for seaborn (plotting preferences)
sns.set()
sns.set_palette("BuPu")

#plot number of fire incidents per district (note this plots all fires for 2012-2015
#for all the districts in the file)
fire.Postcode_district.value_counts().plot(kind='barh', figsize=(12,30))

#now lets visualize the fire data per property category over the years
fig, ax=plt.subplots()
cat_year=pd.crosstab(fire.PropertyCategory,fire.Year)
ax=cat_year.plot(kind='barh',subplots=True,
                               figsize=(10,8),sharex=True,sharey=True
                               ,rot=0)
                               
#segment property catgeories per property type, thid will give us more insight on
#the properties within each category
grouped= fire.PropertyType.groupby(fire['PropertyCategory'])
dwelling=grouped.get_group('Dwelling') 

#since dwelling is th highest fire incidence related property
#it is worth visializing it over the time 
timeddwelling=pd.crosstab(dwelling, fire.Year)
ax1=timeddwelling.plot(kind='barh', subplots=False, rot=0, figsize=(12,14))

#now let's visualize the fire incidences per district per year
dist_year=pd.crosstab(fire.Postcode_district,fire.Year)
axhandles=dist_year.plot(kind='barh',subplots=True,
                               figsize=(16,12),sharex=True,sharey=True
                               ,rot=0)

#let's get some insight on the dwelling per postcode
dwell_district=pd.crosstab(fire.Postcode_district, dwelling)
dwell_district.plot(kind='barh', figsize=(14,12), rot=0)

# Next, let's explore the spatial distribution of fires. 
#We can create a simple crosstab table and look at the count distribution
# Let's try to look at the city-wide 10 top districts in fire incidence and 
#perform a breakdown per property type
top_districts=fire[fire['Postcode_district'].isin(fire['Postcode_district'].value_counts().head(10).index)]
top_properties=fire[fire['PropertyType'].isin(fire['PropertyType'].value_counts().head(10).index)]
top_ten_all=pd.crosstab(top_districts['Postcode_district'], top_properties['PropertyType'])
top_ten_all.plot(kind='barh',figsize=(18,10),stacked=True)

#Shall we need to analyse the trends per year on the top districs and categories
dist_year=pd.crosstab(fire['Year'],top_districts['Postcode_district'])
with sns.color_palette("husl", 10):
    dist_year.plot(marker='o', figsize=(10,12))
dist_year=pd.crosstab(top_districts['Postcode_district'],fire['Year'])
dist_year.plot(kind='bar', subplots=False)

type_year=pd.crosstab(fire['Year'],top_properties['PropertyType'])
with sns.color_palette("husl", 10):
    type_year.plot(marker='o', figsize=(10,15))
type_year=pd.crosstab(top_properties['PropertyType'], fire['Year'])
type_year.plot(kind='barh', subplots=False)

plt.close('all')
