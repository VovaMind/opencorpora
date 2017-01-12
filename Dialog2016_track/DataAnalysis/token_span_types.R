library(class)
library(randomForest)

set.seed(281189)


data <- read.csv('found_objects.csv')

drops <- c("token_id", "token_objects")
word2vec_features_count <- 1000
filteredData <- data[ , !(names(data) %in% drops)]

data$is_test <- as.logical(data$is_test)

rare_output <- subset(as.data.frame(table(data$token_span_types, dnn = ('Value'))), Freq < 5)$Value
is_rare_output = data$token_objects %in% rare_output
data[is_rare_output,]$is_test <- F

boost_model <- randomForest(token_span_types~., data=filteredData[!data$is_test,], mfinal=10)
boost_result <- predict(boost_model, filteredData[data$is_test,])
stats <- filteredData[data$is_test,]$token_span_types == boost_result
print(table(stats))
print(table(filteredData[data$is_test,][!stats,]$token_span_types))
save(boost_model, file="spans_model.bin")
