library(adabag)
library(class)

set.seed(281189)

setwd('C:\\development\\OpenCorpora\\FactExtAutoAssesst\\data')
data <- read.csv('found_objects.csv')

drops <- c("token_id", "token_objects")
word2vec_features_count <- 1000
filteredData <- data[ , !(names(data) %in% drops)]

data$is_test <- as.logical(data$is_test)

boost_model <- boosting(token_span_types~., data=filteredData[!data$is_test,], mfinal=10)
boost_result <- predict(boost_model, filteredData[data$is_test,])
stats <- filteredData[data$is_test,]$token_span_types == boost_result$class
print(table(stats))

save(boost_model, file="spans_model.bin")
