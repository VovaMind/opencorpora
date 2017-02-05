source("classifier.R")

train_data <- read.csv('found_objects.csv')
load("objects_model.bin")
objects_model <- boost_model
load("spans_model.bin")
spans_model <- boost_model

args = commandArgs()
setwd(args[length(args)])

OUTPUT_FILES_COUNT = 5000
for (i in 0:(OUTPUT_FILES_COUNT - 1)) {
        input_file_name <- paste('_features_', as.character(i), '.csv', sep='')
        print(input_file_name)
        data <- read.csv(input_file_name)
		# Fix for randomForest, it requires identical levels in train and test
		for (col_name in colnames(data)) {
			if (col_name != 'token_id' && is.factor(data[,col_name])) {
				data[,col_name] <- factor(as.character(data[,col_name]), 
										levels = levels(train_data[,col_name]))
			}
		}
		data$is_test <- rep(T, nrow(data))
		objects_result <- classify(data, objects_model)
		data$found_objects <- objects_result
		if (is.factor(data$found_objects)) {
			data$found_objects <- factor(as.character(data$found_objects), 
										levels = levels(train_data$found_objects))
		}
        spans_result <- classify(data, spans_model)
        answer = data.frame(id = data$token_id, 
                            objects = as.character(objects_result),
                            spans = as.character(spans_result))
        output_file_name <- paste('_output_', as.character(i), '.csv', sep='')
        write.csv(answer, output_file_name)
}
