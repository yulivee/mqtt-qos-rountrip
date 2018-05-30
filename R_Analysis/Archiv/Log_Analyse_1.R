setwd("/home/lisa/Darmstadt/05_Speicher und Datennetze IoT/Praktikum/Git/mqtt-qos-rountrip/logs/")
df1 <- read.csv(file = "mqtt-roundtrip-qos1-1MByte-10-cycles-client1.log", sep = ",")


#Create the list of log files in the folder
files <- list.files(pattern = "*client1.log", full.names = TRUE, recursive = FALSE)

#library(data.table)
df <- rbindlist(lapply(files, fread, skip=3))


# Paste factor formate -> Character
# then parse it with strptime to POSIXlt and add to Dataframe


options(digits.secs=3) # needs to be set from time to time - otherwise R doesn't allow for ms
#df<-as.data.table(df)

for (i in 1:nrow(df)) {
  #z[i]<-as.POSIXct(strptime(gsub(":", ".", paste(df[i,1],df[i,2])),"%Y-%m-%d %H.%M.%OS"))
  z[i]<-strptime(gsub(":", ".", paste(df[i,1],df[i,2])),"%Y-%m-%d %H.%M.%OS")
}

df<-df[,1:7]
z<-as.POSIXct(z)
df<-cbind(df, z)

# Name DF
colnames = c("Date", "Time", "Action", "Topic", "QoS", "Size", "ID", "Timestamp")
colnames(df)<- colnames


#####################
z<-strptime(gsub(":", ".", paste(df1[,1],df1[,2])),"%Y-%m-%d %H.%M.%OS")
df1[,8]<-as.POSIXct(z1)
t1<-c(1:19)
df1[,8]<-t1
####################


# Difference of max timestamp and min timestamp grouped by ID
# diff <- as.numeric(difftime(), units = "secs"))

times<-as.data.frame(matrix(nrow=10, ncol=2))
colnames = c("rtt", "id")
colnames(times)<- colnames

sentTimes <- subset(df, Action=="sent")
recTimes <- subset(df, Action=="received")

for (i in 1:nrow(sentTimes)) {
 times[i, "id"]<- sentTimes[i,"ID"]
 times[i,"rtt"]<- difftime(recTimes[i,8], sentTimes[i,8])
}







