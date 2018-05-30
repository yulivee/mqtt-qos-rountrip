setwd("/home/lisa/Darmstadt/05_Speicher und Datennetze IoT/Praktikum/Git/mqtt-qos-rountrip/logs/")
options(digits.secs=3) # needs to be set from time to time - otherwise R doesn't allow for ms
library("data.table", lib.loc="~/R/x86_64-pc-linux-gnu-library/3.4")

#Create the list of log files in the folder
files <- list.files(pattern = "*client1.log", full.names = TRUE, recursive = FALSE)
files <- list.files(pattern = "mqtt-roundtrip-qos0-100Byte-30-minutes-client1", full.names = TRUE, recursive = FALSE)



# Create df according to several pattern options
# files_qos0 = intersect(list.files(pattern = "client1.log"), list.files(pattern = "qos0"))
# files_qos1 = intersect(list.files(pattern = "client1.log"), list.files(pattern = "qos1"))
# files_qos2 = intersect(list.files(pattern = "client1.log"), list.files(pattern = "qos2"))


# Read the logs into dataFrames and bind
df <- rbindlist(lapply(files, fread))

#df_qos0 <- rbindlist(lapply(files_qos0, fread))
#df_qos1 <- rbindlist(lapply(files_qos1, fread))
#df_qos2 <- rbindlist(lapply(files_qos2, fread))


# Read the logs into separate dataFrames
for (i in 1:length(files)) {
  x <- rbindlist(lapply(files[i], fread))
  assign(paste("df", i), x)
}


# Substitute ":" and "." in Order to apply strptime with %OS for ms
# Save as POSIXc because POSIXlt saves row for each %

z<-c(as.POSIXct("2018-05-18 14:01:41.264 CEST"))
newID<-c()

# Configure df (i.e x<- `df 52`, df_qos1, df_all)
x<-df
for (i in 1:nrow(x)) {
  z[i]<-as.POSIXct(strptime(gsub(":", ".", paste(x[i,1],x[i,2])),"%Y-%m-%d %H.%M.%OS"))
  newID[i]<-paste(x[i,4], x[i,7])
}
df<-cbind(df, z, newID)

# Name DF
#colnames(df_qos1)<- c("Date", "Time", "Action", "Topic", "QoS", "Size", "ID", "Timestamp")
colnames(df)<- c("Date", "Time", "Action", "Topic", "QoS", "Size", "ID", "Timestamp", "newID")

#################
# Calculate RTT #
#################

# Create DF to hold RTT
times<-as.data.frame(matrix(nrow=2000, ncol=6))
colnames(times)<- c("sent", "s_newid", "rec", "r_newid", "rtt", "id")

# Change Dataformate für TS Cols 
times[,1] <-as.POSIXct(strptime(times[, "sent"],"%Y-%m-%d %H.%M.%OS"))
times[,3] <-as.POSIXct(strptime(times[, "rec"],"%Y-%m-%d %H.%M.%OS"))


# Subsets sent and received
sentTimes <- subset(df, Action=="sent")
recTimes <- subset(df, Action=="received")

# Move TS to new DF
for (i in sentTimes$ID) {
  times[i, "sent"]<- sentTimes[which(sentTimes$ID == i),"Timestamp"]
  times[i, "id"]<- sentTimes[which(sentTimes$ID == i),"ID"]
  times[i, "s_newid"]<- sentTimes[which(sentTimes$ID == i),"newID"]
}

for (i in recTimes$ID) {
  times[i, "rec"]<- recTimes[which(recTimes$ID == i),"Timestamp"]
  times[i, "id"]<- recTimes[which(recTimes$ID == i),"ID"]
  times[i, "r_newid"]<- sentTimes[which(sentTimes$ID == i),"newID"]
}

# Calculate Difference
for (i in 1:nrow(times)) {
  times[i,"rtt"]<- difftime(times[i,3], times[i,1])
}

#############
### tests ###
#############
df1 <- read.csv(file = "mqtt-roundtrip-qos1-1MByte-10-cycles-client1.log", sep = ",")
z1<-strptime(gsub(":", ".", paste(df1[,1],df1[,2])),"%Y-%m-%d %H.%M.%OS")
df1[,8]<-as.POSIXct(z1)

for (i in 1:nrow(df1)) {
  df1[i,9]<-paste(df1[i,4], df1[i,7])
}
colnames(df1)<- c("Date", "Time", "Action", "Topic", "QoS", "Size", "ID", "Timestamp", "newID")

for (i in 1:nrow(sentTimes)) {
  times[i, "id"]<- sentTimes[i,"ID"]
  times[i,"rtt"]<- difftime(recTimes[i,8], sentTimes[i,8])
}


########### Schreib ID in Array und nutze ihn für Colnames ##########
v<-c()
for (i in sentTimes$newID) {
  #v<-rbind(v,i)
  v[i] <-i
}
#v<-cbind(v)
row.names(sentTimes)<-v[1,]
row.names(times)<-v[1,]



#############
#df<-as.data.table(df)

