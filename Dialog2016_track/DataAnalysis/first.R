set.seed(281189)

setwd('C:\\development\\OpenCorpora\\FactExtAutoAssesst')
data <- read.csv('data\\MarkupData.csv')

library(adabag)
library(class)

tokenIds <- data$token_id
tokenTexts <- data$token_text
drops <- c("token_id", "token_text")
#filteredData <- filteredData[ , !(names(filteredData) %in% drops)]
filteredData <- data[ , !(names(data) %in% drops)]

n = nrow(filteredData)
random_seed <- sample(0:10, n, replace=T)
test <- filteredData[random_seed >= 5,]
train <- filteredData[random_seed < 5,]

testTokenIds <- tokenIds[random_seed >= 5]
testTokenTexts <- tokenTexts[random_seed >= 5]
        
correct <- test$token_objects
test$token_objects <- rep("XZ", nrow(test))

boost_model <- boosting(token_objects~., data=train, mfinal=6)
boost_result <- predict(boost_model, test)
#print(table(boost_result$class,correct))
temp <- correct == boost_result$class
print(table(temp))

#write.table(table(correct, boost_result$class), 
#            file = "data\\first_result.txt")
#cat(table(correct, boost_result$class), file = "data\\first_result.txt", sep = '\n')
options(width = 200)
capture.output(print(table(correct, boost_result$class), print.gap=3), 
               file="data\\first_result.txt")

badMy <- boost_result$class[correct != boost_result$class]
badCorrect <- correct[correct != boost_result$class]
badTokenIds <- testTokenIds[correct != boost_result$class]
badTexts <- testTokenTexts[correct != boost_result$class]
#print(badTokenIds)

bad_df <- data.frame(my = badMy, correct = badCorrect, tokenId = badTokenIds, 
                     text = badTexts)
capture.output(print(bad_df, print.gap=3), 
               file="data\\first_errors.txt")
