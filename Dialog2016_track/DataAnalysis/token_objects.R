library(adabag)
library(class)

set.seed(281189)

setwd('C:\\development\\OpenCorpora\\FactExtAutoAssesst\\data')
data <- read.csv('MarkupData.csv')
data <- data[,!(names(data) %in% c("token_text"))]

drops <- c("token_id", "mystem_info", "token_span_types")
word2vec_features_count <- 1000
drops <- c(drops,paste("word2vec_feature_", as.character(0:word2vec_features_count), sep=""))
filteredData <- data[ , !(names(data) %in% drops)]

n = nrow(filteredData)
random_seed <- sample(0:10, n, replace=T)
data$is_test <- random_seed >= 5

boost_model <- boosting(token_objects~., data=filteredData[!data$is_test,], mfinal=10)
boost_result <- predict(boost_model, filteredData[data$is_test,])
stats <- filteredData[data$is_test,]$token_objects == boost_result$class
print(table(stats))

data$found_objects <- filteredData$token_objects
data[data$is_test,]$found_objects <- boost_result$class

save(boost_model, file="objects_model.bin")
write.csv(data, "found_objects.csv", row.names=FALSE)
