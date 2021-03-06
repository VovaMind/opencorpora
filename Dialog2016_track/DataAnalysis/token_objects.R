source("classifier.R")
set.seed(281189)

data <- read.csv('MarkupData.csv')
data <- data[,!(names(data) %in% c("token_text"))]

drops <- c("token_id", "token_span_types")
print(nrow(data))
print(ncol(data))

filteredData <- data[ , !(names(data) %in% drops)]

n = nrow(filteredData)
random_seed <- sample(0:9, n, replace=T)
data$is_test <- random_seed >= 10 

rare_output <- subset(as.data.frame(table(data$token_objects, dnn = ('Value'))), Freq < 5)$Value
is_rare_output = data$token_objects %in% rare_output
data[is_rare_output,]$is_test <- F

boost_model <- train_classifier(filteredData, T)
boost_result <- classify(filteredData, boost_model)
stats <- filteredData[data$is_test,]$token_objects == boost_result
print(table(stats)) 
print(table(filteredData[data$is_test,][!stats,]$token_objects))

data$found_objects <- filteredData$token_objects
data[data$is_test,]$found_objects <- boost_result


save(boost_model, file="objects_model.bin")
write.csv(data, "found_objects.csv", row.names=FALSE)
