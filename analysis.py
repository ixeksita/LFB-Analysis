import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

dateparse = (lambda x: pd.to_datetime(x, format='%d-%b-%y'))
fire=pd.read_csv('LFB.csv', parse_dates=['DateOfCall'], 
               date_parser=dateparse)

fire['Year'] = fire['DateOfCall'].map(lambda x: x.year)


sns.set_style('dark')

#plot number of fire incidents per district
fire.Postcode_district.value_counts().plot(kind='barh', figsize=(8,10))

#now lets visualize the fire data per property category over the years
cat_year=pd.crosstab(fire.PropertyCategory,fire.Year)
axhandles=cat_year.plot(kind='barh',subplots=True,
                               figsize=(10,8),sharex=True,sharey=True
                               ,rot=0)
                               
#visualize the fire data per property type
type_year=pd.crosstab(fire.PropertyType,fire.Year)
axhandles=type_year.plot(kind='barh',subplots=True,
                               figsize=(16,12),sharex=True,sharey=True
                               ,rot=0)
                               
#segment property catgeories per property type
grouped= fire.PropertyType.groupby(fire['PropertyCategory'])
dwelling=grouped.get_group('Dwelling')

#since dwelling is th highest fire incidence related property
#it is worth visializing it over the time 
grouped= fire['Year', 'PropertyType'].groupby(fire['PropertyCategory'])
dwelling=grouped.get_group('Dwelling')

timeddwelling=pd.crosstab(dwelling, fire.Year)
ax1=timeddwelling.plot(kind='barh', subplots=False, rot=0)

#district per year
dist_year=pd.crosstab(fire.Postcode_district,fire.Year)
axhandles=dist_year.plot(kind='barh',subplots=True,
                               figsize=(16,12),sharex=True,sharey=True
                               ,rot=0)

#dwelling per postcode
dwell_district=pd.crosstab(fire.Postcode_district, dwelling)
dwell_district.plot(kind='barh', figsize=(14,12), rot=0)
ddt=dwell_district.groupby(fire.Year)

#heatmap to look how data varies per district 
ax = plt.subplots()
heatData = []
yLoopCount=0
yearName = []
yearName = ['2012','2013','2014', '2015']
for yLoop in range(2012,2015):
    heatData.append([])
    for dLoop in range(7):
        allData2 = fire[(fire.index.Year == yLoop) & (fire.index.PropertyCategory == dLoop)]
        heatData[yLoopCount].append(sum(allData2['z'].values))
        yLoopCount+=1
                
#normlise
heatData = np.array(heatData)/np.max(np.array(heatData))
sns.heatmap(heatData, annot=True, yticklabels=yearName);
