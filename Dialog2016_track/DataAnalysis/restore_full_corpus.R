library(adabag)
library(class)

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
        objects_result <- predict(objects_model, data)
        data$found_objects <- objects_result$class
        data$is_test <- rep(T, nrow(data))
        spans_result <- predict(spans_model, data)
        answer = data.frame(id = data$token_id, 
                            objects = as.character(objects_result$class),
                            spans = as.character(spans_result$class))
        output_file_name <- paste('_output_', as.character(i), '.csv', sep='')
        write.csv(answer, output_file_name)
}
