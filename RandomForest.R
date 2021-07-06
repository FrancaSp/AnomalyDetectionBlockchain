library(ggplot2)
library(dplyr)

library(dygraphs)
library(xts)


etc19 <-  read.csv('/Users/francaspeth/Google Drive/Masterarbeit/Share/ETC_block_2019_alldata.csv')
etc20 <- read.csv('/Users/francaspeth/Google Drive/Masterarbeit/Share/ETC_block_2020_alldata.csv')

data<-rbind(etc19, etc20)
rm(etc19,etc20)

normalize <- function(x) {
  return ((x - min(x)) / (max(x) - min(x)))
}

# cleanup <- function(x) {
#   x$date <- as.Date(x$timestamp)
#   x$time <- format(as.POSIXct(x$timestamp), format = "%H:%M:%S") 
#   # colu <- c('number', 'nonce', 'sha3_uncles', 'miner', 'difficulty', 'total_difficulty', 
#   #           'size', 'gas_limit', 'gas_used','uncles','date', 'time')
#   # x<- x %>% dplyr::select(colu)
#   # x$size <- normalize(x$size)
#   # x$gas_limit <- normalize(x$gas_limit)
#   # x$gas_used <- normalize(x$gas_used)
#   # x$difficulty <- normalize(x$difficulty)
#   # x$total_difficulty <- normalize(x$total_difficulty)
#   # x$nonce <- normalize(x$nonce)
#   return(x)
# }
# 
# ETC19<-cleanup(ETC19)
# at<- dplyr::filter(ETC19, number <= 7261690 & number>= 7245623)
# #at <- at %>% filter(time>='19:19:03')
# at$attack <- 1
# noattack <- dplyr::filter(ETC19, date >='2019-01-10' & date <='2019-01-30')
# noattack$attack <- 0
# at <- all_attacks %>% 
#   select( 'difficulty',  'miner', 'total_difficulty','number', 'extra_data', #'mean_total_difficulty'# 'nonce'
#           'size', 'gas_limit', 'gas_used')#,'uncles','sha3_uncles') 
# 
# noat <- noattacks %>% 
#   select( 'difficulty',  'miner', 'total_difficulty','number', 'extra_data',# 'mean_total_difficulty',# 'nonce'
#           'size', 'gas_limit', 'gas_used')#,'uncles','sha3_uncles') 
# data <- rbind(at, noattack)

data[is.na(data)] <- 0
X <- data %>% 
  select( 'difficulty', 'total_difficulty', "avg_nonce","num_uncles", "total_num_uncles",
          'size', 'gas_limit', 'gas_used', "num_tx", "avg_tx_value", 'num_uncles', 'total_num_uncles', 'num_emptyblocks',
          'dummy_miner_before','dummy_miner_count', 'hashrate', 'block_time')#,'uncles','sha3_uncles') 
y <- data$label
y<- as.factor(y)

set.seed(248)
index <- caret::createDataPartition(y, p=0.75, list=FALSE)
X_train <- X[ index, ]
X_test <- X[-index, ]
y_train <- y[index]
y_test <- y[-index]

library(randomForest)
library(caret)

# Train the model 
regr2 <- randomForest(x = X_train, y = y_train, maxnodes = 100, ntree = 100, replace = TRUE)

# Make prediction
predictions <- predict(regr2, X_test)

# View results of prediction 
table(predictions,y_test) 
confusionMatrix(predictions,y_test)

library(corrplot)
library(RColorBrewer)
M <-cor(X)
corrplot(M, type="upper",order="hclust", col=brewer.pal(n=8, name="RdYlBu"),
         tl.col = 'black')

varImpPlot(regr2)

local <- '/Volumes/Thesis/BitcoinGold_csv/'
btg1 <- read.csv(paste(local,'BTG_Train1_labeled.csv', sep=''))
btg2 <- read.csv(paste(local,'BTG_Train2_labeled.csv', sep=''))
btg3 <- read.csv(paste(local,'BTG_Train3_labeled.csv', sep=''))
btg4 <- read.csv(paste(local,'BTG_Test1_labeled.csv', sep=''))
btg5 <- read.csv(paste(local,'BTG_Test2_labeled.csv', sep=''))

btg  <- rbind(btg1,btg2,btg3, btg4,btg5)
# wallethack <- filter(btg, height >= 501743 & height <= 501889)
# majority18 <- filter(btg, height  >= 528735 & height <= 529048)
# majority20 <- filter(btg,height  >= 617745 & height <=  617757 |
#                        height  >= 617776 & height <= 617792)
# majority18$label <- 1
# majority20$label <- 1
# wallethack$label <- 2
# 
# noattacks <- filter(btg, height  < 528735 | height > 529048  &
#                       height  < 617745 | height >  617757 &
#                       height  < 617776 | height > 617792)
# 
# noattacks <- filter(noattacks, height < 501743 | height > 501889)
# 
# noattacks$label <- 0
# 
# btg = rbind(noattacks,majority18,majority20, wallethack)
btg = btg[order(btg$height),]

X <- btg %>% 
  select("confirmations", "strippedsize",  "difficulty", "size", "weight",
         "nTx", "total_reward", "num_in", "num_out",
         "btg_out", "hashrate", "block_time" ) 
y <- btg$label
y<- as.factor(y)

set.seed(248)
index <- caret::createDataPartition(y, p=0.75, list=FALSE)
X_train <- X[ index, ]
X_test <- X[-index, ]
y_train <- y[index]
y_test <- y[-index]

library(randomForest)
library(caret)

# Train the model 
regr2 <- randomForest(x = X_train, y = y_train, maxnodes = 100, ntree = 100, replace = TRUE)

# Make prediction
predictions <- predict(regr2, X_test)

# View results of prediction 
table(predictions,y_test) 
confusionMatrix(predictions,y_test)

library(corrplot)
library(RColorBrewer)
M <-cor(X)
corrplot(M, type="upper",order="hclust", col=brewer.pal(n=8, name="RdYlBu"),
         tl.col = 'black')

varImpPlot(regr2)
