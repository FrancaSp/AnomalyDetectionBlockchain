library(ggplot2)
library(dplyr)

library(dygraphs)
library(xts)

library(randomForest)
library(caret)


userdf  = read.csv('/Volumes/Thesis/BlockchainData/ETC/ETC_UserData_labeled_2018_2020.csv')

X <- userdf %>% 
  select('in_etc', 'mean_in_etc', 'cum_gas_used', 'out_etc', 'mean_out_etc',
         'numsenttx', 'avg_gas_limit',
         'avg_gas_price', 'avg_num_of_blocks_between_intx',
         'avg_num_of_blocks_between_outtx',
         'median_num_of_blocks_between_outtx',
         'median_num_of_blocks_between_intx') 
y <- userdf$label
y<- as.factor(y)
set.seed(934)
index <- caret::createDataPartition(y, p=0.75, list=FALSE)
X_train <- X[ index, ]
X_test <- X[-index, ]
y_train <- y[index]
y_test <- y[-index]
# Train the model 
regr2 <- randomForest(x = X_train, y = y_train, maxnodes = 100, ntree = 100, replace = TRUE)

# Make prediction
predictions <- predict(regr2, X_test)

# View results of prediction 
table(predictions,y_test) 
confusionMatrix(predictions,y_test)
varImpPlot(regr2)


