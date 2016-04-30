# -*- coding: utf-8 -*-
#Exploratory analysis for LFB data
#This code is intended to provide an overview of the data contained in LFBincidents.csv
#corresponding to the fires registered between 2012 and 2015
#for more information on the dataset visit: www.london-fire.gov.uk

#Loading modules, libraries, etc. 
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Reading the data from the csv and parsing the dates
#Please note the name of the given LFB file was changed 
dateparse = (lambda x: pd.to_datetime(x, format='%d-%b-%y'))
fire=pd.read_csv('LFB.csv', parse_dates=['DateOfCall'], 
               date_parser=dateparse)

#Obtain the years from the date of call 
fire['Year'] = fire['DateOfCall'].map(lambda x: x.year)
fire['Month'] = fire['DateOfCall'].map(lambda x: x.month)

#Set parameters for seaborn (plotting preferences)
sns.set()
sns.set_palette("BuPu")

#Plot number of fire incidents per district 
#(note this plots all fires for 2012-2015
#for all the districts in the file), it is too much info for my liking
fire.Postcode_district.value_counts().plot(kind='barh', figsize=(12,36))
plt.title('Fire incidences per district \n 2012-2015')
plt.savefig('fire_district-all.png')

#Now lets visualize the fire data per property category over the years
fig, ax=plt.subplots()
cat_year=pd.crosstab(fire.PropertyCategory,fire.Year)
ax=cat_year.plot(kind='barh',subplots=True,
                               figsize=(10,8),sharex=True,sharey=True
                               ,rot=0)
plt.savefig('Plots/Property_category_per_year.png')

#Segment property catgeories per property type, 
#this will give us more insight on
#the actual properties within each category
grouped= fire.PropertyType.groupby(fire['PropertyCategory'])
dwelling=grouped.get_group('Dwelling') 

#Since dwelling is the highest fire incidence related property
#it is worth visualizing it over the time 
timeddwelling=pd.crosstab(dwelling, fire.Year)
ax1=timeddwelling.plot(kind='barh', subplots=False, rot=0, figsize=(12,14))
plt.title("Dwelling incidences per year")
plt.savefig('Plots/dwelling_per_year.png')

#Now let's visualize the fire incidences per district per year
#too much 
dist_year=pd.crosstab(fire.Postcode_district,fire.Year)
axhandles=dist_year.plot(kind='barh',subplots=True,
                               figsize=(16,12),sharex=True,sharey=True
                               ,rot=0)
plt.title('Number of fire incidences per postcode district per year')

#Let's get some insight on the dwelling per postcode
#too much
dwell_district=pd.crosstab(fire.Postcode_district, dwelling)
dwell_district.plot(kind='barh', figsize=(14,12), rot=0)
plt.title('Dwelling fire incidences per postcode area')

# Next, let's explore the spatial distribution of fires. 
#We can create a simple crosstab table and look at the count distribution
# Let's try to look at the city-wide 10 top districts in fire incidence and 
#perform a breakdown per property type
top_districts=fire[fire['Postcode_district'].isin(fire['Postcode_district'].value_counts().head(10).index)]
top_properties=fire[fire['PropertyType'].isin(fire['PropertyType'].value_counts().head(10).index)]
top_properties.plot(kind='barh', figsize=(18,10))
plt.title('Top ten type of fire incidences per year')
plt.ssavefig('Plots/type_year.png')

top_ten_all=pd.crosstab(top_districts['Postcode_district'], top_properties['PropertyType'])
top_ten_all.plot(kind='barh',figsize=(18,10),stacked=True)
plt.title('Number of incidences for the top 10 type of property \n in the postcodes with the higer fire incidence')
plt.savefig('Plots/top_ten_per_district.png')

#Shall we need to analyse the trends per year on the top districs and categories
dist_year=pd.crosstab(fire['Year'],top_districts['Postcode_district'])
with sns.color_palette("husl", 10):
    dist_year.plot(marker='o', figsize=(10,12))
dist_year=pd.crosstab(top_districts['Postcode_district'],fire['Year'])
dist_year.plot(kind='bar', subplots=False)
plt.title('Fire trends per district per year (total number of incidences)')
plt.savefig('Plots/trends_perdistrict.png')

type_year=pd.crosstab(fire['Year'],top_properties['PropertyType'])
with sns.color_palette("husl", 10):
    type_year.plot(marker='o', figsize=(10,15))
type_year=pd.crosstab(top_properties['PropertyType'], fire['Year'])
type_year.plot(kind='barh', subplots=False)
plt.title('Fire trends per property type per year (total number of incidences)')
plt.savefig('Plots/trends_pertype.png')

plt.close('all')
