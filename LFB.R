library(dplyr)
library(ggmap)
library(ggplot2)
library(readr)
fire<- read.csv("LFB.csv")
London <- get_map(location=c(-1.25, 51.13, 0.849, 51.76),  color = "bw", maptype = "roadmap", zoom=10)

#Add a column for the years 
fire$DateOfCall<-as.Date(fire$DateOfCall, format="%d-%b-%y")
fire["Year"]<-as.numeric(format(fire$DateOfCall,"%y"))
fire$Year<-fire$Year+2000

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

#contour plots
contour<-stat_density2d(aes(x=Lon, y=Lat, fill=..level..,alpha=..level..)
                        ,size=0.1,data=filter(fire,PropertyType=='Car '),
                        geom='polygon')

cmap<-ggmap(London, extent='device', legend="bottomleft") + contour +
  scale_alpha_continuous(range=c(0.3,0.55), guide='none') +
  scale_fill_continuous(low='light blue', high='dark magenta')
ggsave("London_car.png", cmap, width=14, height=10, units='in')

#########note add for loop on the property types (unique(top10))
#### then create a heatmap for each
#### divide hthe fire in two and run test then final model 

#prepare the data set, the data corresponding to 2012 will be used for training purposes and the rest 
#for the actual prediction
train<-fire[fire$Year=="2012",c("PropertyType", "Lat", "Lon")]
years=c(2012,2013,2014,2015)
test<-fire[fire$Year %in% years,c("PropertyType", "Lat", "Lon")]

nb_model<-naiveBayes(PropertyType~., data=train)

######Creating the final model
#This is again assuming that a fire is likely to ocurr only in locations
#where a fire has been previously observed

finalmodel<- naiveBayes(PropertyType~., data=test)
predictF<-predict(finalmodel, test)
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
predp<-ggmap(London)+
  geom_point(data=top10p, aes(x=Lon, y=Lat, color=factor(PropertyType_pred)), alpha=0.10) +
  guides(colour = guide_legend(override.aes = list(alpha=1.0, size=2.3),
                               title="Predicted Fire: Property Type")) +
  scale_colour_brewer(type="qual",palette="Set3") + 
  ggtitle("Type of property type fire per area based on \n
          previously observed fire areas") +
  theme_light(base_size=20) +
  theme(axis.line=element_blank(),
        axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        axis.title.x=element_blank(),
        axis.title.y=element_blank())