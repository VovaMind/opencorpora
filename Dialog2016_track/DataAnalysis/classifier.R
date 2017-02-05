library(class)
library(randomForest)
library(adabag)

# 0 - randomForest
# 1 - adaboost
# 2 - bagging
CLASSIFIER_TYPE <- 0

train_classifier <- function(data, is_objects) {
	if (CLASSIFIER_TYPE == 0) {
		if (is_objects) {
			randomForest(token_objects~., data=data[!data$is_test,], mfinal=10)
		} else {
			randomForest(token_span_types~., data=data[!data$is_test,], mfinal=10)
		}
	} else if (CLASSIFIER_TYPE == 1) {
		if (is_objects) {
			boosting(token_objects~., data=data[!data$is_test,], mfinal=10)
		} else {
			boosting(token_span_types~., data=data[!data$is_test,], mfinal=10)
		}
	} else {
		if (is_objects) {
			bagging(token_objects~., data=data[!data$is_test,], mfinal=10)
		} else {
			bagging(token_span_types~., data=data[!data$is_test,], mfinal=10)
		}
	}
}

classify <- function(data, model) {
	result <- predict(model, data[data$is_test,])
	if (CLASSIFIER_TYPE == 0) {
		result
	} else {
		result$class
	}
}
