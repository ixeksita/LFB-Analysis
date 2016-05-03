library(dplyr)
library(ggmap)
library(ggplot2)
library(readr)
library(e1071)
fire<- read.csv("LFB.csv")
London <- get_map(location=c(-1.25, 51.13, 0.849, 51.76),  color = "bw", maptype = "roadmap", zoom=10)

#Add a column for the years 
fire$DateOfCall<-as.Date(fire$DateOfCall, format="%d-%b-%y")
fire["Year"]<-as.numeric(format(fire$DateOfCall,"%y"))
fire$Year<-fire$Year+2000
fire["Day"]<-as.numeric(format(fire$DateOfCall,"%d"))

#Loading the coordinates 
coord<-read.csv("BNGandLatLon.csv")
fire["Lon"]<-coord$Lon
fire["Lat"]<-coord$Lat

#Count the incidences per property type
counts<- summarise(group_by(fire,PropertyType), Counts=length(PropertyType))
counts<- counts[order(-counts$Counts),]

#Identifying the top PropertyCategories
top10<-fire[fire$PropertyType %in% counts$PropertyType[c(1:10,1)],]

#Plotting the top on the map
p<-ggmap(London)+
  geom_point(data=top10, aes(x=Lon, y=Lat, color=factor(PropertyType)), alpha=0.10) +
  guides(colour = guide_legend(override.aes = list(alpha=1.0, size=2.3),
                               title="Fire: Property Type")) +
  scale_colour_brewer(type="qual",palette="Set3") + 
  ggtitle("Type of properties with the higher reported \n
          incidence in London (2012-2015)") +
  theme_light(base_size=20) +
  theme(axis.line=element_blank(),
        axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        axis.title.x=element_blank(),
        axis.title.y=element_blank())
ggsave("London_top_crimes.png", p, width=14, height=10, units='in')

count<-0
label<-'.png'
#contour plots
for(i in unique(top10$PropertyType)){
  gsub("/","-",i, fixed=TRUE) 
  contour<-stat_density2d(aes(x=Lon, y=Lat, fill=..level..,alpha=..level..)
  ,size=0.1,data=filter(fire,PropertyType==i),
  geom='polygon')

  cmap<-ggmap(London, extent='device', legend="bottomleft") + contour +
    scale_alpha_continuous(range=c(0.3,0.55), guide='none') +
    scale_fill_continuous(low='light blue', high='dark magenta')+
    ggtitle(paste(alpha="Heatmap for fire incidences of type:",i))
  count<-count+1
  Filename<-paste(count,label, collapse="-")
  ggsave(Filename, cmap, width=14, height=10, units='in')
}


#prepare the data set, the data corresponding to 2012 will be used for training purposes and the rest 
#for the actual prediction
train_days<-c(1:7, 15:21)
test_days<-c(8:14, 22:31)

train<-fire[fire$Day %in% train_days, c("PropertyType", "Lat", "Lon")]
test<-fire[fire$Day %in% test_days, c("PropertyType", "Lat", "Lon")]

#creating the model
nb_model<-naiveBayes(PropertyType~., data=train, laplace=3)
predictF<- predict(nb_model, test )
vec<- as.character(predictF)
dfP<-data.frame(vec)

#adding the prediction to the complete set
test["PropertyType_pred"]<-dfP

#Count the incidences per property type (predicted)
pcounts<- summarise(group_by(test,PropertyType_pred), Counts=length(PropertyType_pred))
pcounts<- pcounts[order(-pcounts$Counts),]

#Identifying the top PropertyCategories
top10p<-test[test$PropertyType_pred %in% pcounts$PropertyType_pred[c(1:10,1)],]

#Plotting the prediction 
count<-0
label<-'pred.png'
#contour plots
for(i in unique(top10p$PropertyType_pred)){
  gsub("/","-",i, fixed=TRUE) 
  contour<-stat_density2d(aes(x=Lon, y=Lat, fill=..level..,alpha=..level..)
                          ,size=0.1,data=filter(top10p,PropertyType_pred==i),
                          geom='polygon')
  
  cmap<-ggmap(London, extent='device', legend="bottomleft") + contour +
    scale_alpha_continuous(range=c(0.3,0.55), guide='none') +
    scale_fill_continuous(low='light blue', high='dark magenta')+
    ggtitle(paste(alpha="Heatmap for predicted fire incidences of type:",i))
  count<-count+1
  Filename<-paste(count,label, collapse="-")
  ggsave(Filename, cmap, width=14, height=10, units='in')
}
