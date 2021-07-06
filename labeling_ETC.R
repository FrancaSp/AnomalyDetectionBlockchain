library(dplyr)
library(ggplot2)
## set local dir for data ## 
local <- '/Users/francaspeth/Google Drive/Masterarbeit/Share/'
## load the data ##
etc18<-read.csv(paste(local,'ETC_block_2018_withuncles.csv', sep=''))
etc18 <- etc18[,-2]
etc18$label <- 0 
write.csv(etc18,paste(local,'ETC_block_2018_withuncles.csv', sep=''))
rm(etc18)

etc19<-read.csv(paste(local,'ETC_block_2019_withuncles.csv', sep=''))
etc19 <- etc19[,-2]
attack <- dplyr::filter(etc19, number >= 7245623 & number <= 7261690)
noattack <- dplyr::filter(etc19, number < 7245623 | number > 7261690)
attack$label <- 1
noattack$label <- 0 
etc19 <- rbind(attack, noattack)
write.csv(etc19,paste(local,'ETC_block_2019_withuncles.csv', sep=''))
rm(etc19)

etc20<-read.csv(paste(local,'ETC_block_2020_withuncles.csv', sep=''))
etc20 <- etc20[,-2]

attack <- dplyr::filter(etc20, number >= 10904146 & number <= 10907740 
                        | number >= 10935623 & number <= 10939858
                        | miner == "1.35983106511221e+47")
lastat<- c(filter(attack, miner == "1.35983106511221e+47")$number)

## since the last attack is not analysed well enough we try to analyse the beginning and end of the attack ##
last<- filter(etc20, number >= 11091000 & number <= 11097920)  
ggplot(last, aes(x=last$number, y=last$size)) + geom_line()
ggplot(last, aes(x=last$number, y=last$miner)) + geom_line()
ggplot(last, aes(x=last$number, y=last$total_num_uncles)) + geom_line()
ggplot(last, aes(x=last$number, y=last$num_uncles)) + geom_line()
ggplot(last, aes(x=last$number, y=last$num_tx)) + geom_line()
ggplot(last, aes(x=last$number, y=last$gas_used)) + geom_line()
ggplot(last, aes(x=last$number, y=last$avg_nonce)) + geom_line()
ggplot(last, aes(x=last$number, y=last$avg_tx_value)) + geom_line()

noattack <- dplyr::filter(etc20, number < 10904146 | number > 10907740 
                          & number < 10935623 | number > 10939858
                          & miner != "1.35983106511221e+47")
attack$label <- 1
noattack$label <- 0 
etc20 <- rbind(attack, noattack)
write.csv(etc20,paste(local,'ETC_block_2020_withuncles.csv', sep=''))


local <- '/Volumes/Thesis/BlockchainData/ETC/'

## Transactions 2018 ## 
reducefeatures<-function(local, filename){
  tx <- read.csv(paste(local,filename, sep=''), colClasses =  c('NULL','NULL', NA,NA,NA,NA,'NULL',NA,
                                                                             'NULL','NULL',NA,NA,'NULL',NA,'NULL',
                                                                             'NULL','NULL','NULL','NULL', 'NULL',NA,
                                                                             'NULL','NULL','NULL'))
  tx[is.na(tx)]<-0
  tx <- filter(tx, creates == 0)
  return(tx)
}
tx1 <- reducefeatures(local, 'ETC_tx_12_2018.csv')
tx2 <- reducefeatures(local, 'ETC_tx_9_11_2018.csv')
tx3 <- reducefeatures(local, 'ETC_tx_6_8_2018.csv')
tx4 <- reducefeatures(local, 'ETC_tx_2_5_2018.csv')
tx5 <- reducefeatures(local, 'ETC_tx_1_2018.csv')
tx <- rbind(tx1,tx2,tx3,tx4, tx5)
tx <- tx[order(tx$block_number),]
write.csv(tx, paste(local,'ETC_tx_2018_reduced.csv', sep=''),row.names = FALSE)

## Transactions 2019 ## 
tx1 <- reducefeatures(local, 'ETC_tx_1_2019.csv')
tx2 <- reducefeatures(local, 'ETC_tx_2_5_2019.csv')
tx3 <- reducefeatures(local, 'ETC_tx_3_4_2019.csv')

tx4 <- reducefeatures(local, 'ETC_tx_6_8_2019.csv')
tx5 <- reducefeatures(local, 'ETC_tx_9_12_2019.csv')

tx <- rbind(tx1,tx2,tx3,tx4, tx5)
attack <- dplyr::filter(tx, block_number >= 7245623 & block_number <= 7261690)
attack$label <- 1
noattack <- dplyr::filter(tx, block_number < 7245623 | block_number > 7261690)
noattack$label <- 0 
tx <- rbind(attack, noattack)
tx<- rbind(tx, tx4, tx5)
tx <- tx[order(tx$block_number),]
write.csv(tx, paste(local,'ETC_tx_2019_reduced.csv', sep=''),row.names = FALSE)

## Transactions 2020 ## 
tx1 <- reducefeatures(local, 'ETC_tx_01_6_2020.csv')
tx1$label <- 0 
tx2 <- reducefeatures(local, 'ETC_tx_7_10_2020.csv')
attack <- dplyr::filter(tx2, block_number >= 10904146 & block_number <= 10907740 
                        | block_number >= 10935623 & block_number <= 10939858 
                        | block_number %in% lastat)
attack$label <- 1
noattack <- dplyr::filter(tx2, block_number < 10904146 | block_number > 10907740 
                          & block_number < 10935623 | block_number > 10939858
                          & !block_number %in% lastat)
noattack$label <- 0
tx <- rbind(attack,noattack,tx1)
tx <- tx[order(tx$block_number),]
write.csv(tx, paste(local,'ETC_tx_2020_reduced.csv', sep=''),row.names = FALSE)

