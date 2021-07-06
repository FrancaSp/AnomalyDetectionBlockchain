library(dplyr)
library(ggplot2)

local <- '/Volumes/Thesis/BitcoinGold_csv/'

btg1 <- read.csv(paste(local,'blocks1.csv', sep=''))
btg2 <- read.csv(paste(local,'blocks2.csv', sep=''))
btg3 <- read.csv(paste(local,'blocks3.csv', sep=''))
btg4 <- read.csv(paste(local,'blocks4.csv', sep=''))
btg5 <- read.csv(paste(local,'blocks5.csv', sep=''))

btg  <- rbind(btg1,btg2,btg3, btg4,btg5)
rm(btg1,btg2,btg3,btg4,btg5)
wallethack <- filter(btg, height >= 501743 & height <= 501889)
majority18 <- filter(btg, height  >= 528735 & height <= 529048)
majority20 <- filter(btg,height  >= 617745 & height <=  617757 |
                     height  >= 617776 & height <= 617792)
majority18$label <- 1
majority20$label <- 1
wallethack$label <- 2

noattacks <- filter(btg, height  < 528735 | height > 529048  &
                      height  < 617745 | height >  617757 &
                      height  < 617776 | height > 617792)

noattacks <- filter(noattacks, height < 501743 | height > 501889)

noattacks$label <- 0

#t1 <- filter(noattacks, height >= min(noattacks$height) & height <= 501500)
t1 <- filter(noattacks, height >= 502200 & height <= 526000)
t2 <- filter(noattacks, height >= 531000 & height <= 610000)
t3 <- filter(noattacks, height >=622000 & height <= max(noattacks$height))
test1 <- rbind(filter(noattacks, height >  526000 & height < 528735), 
               majority18, filter(noattacks, height > 529048 & height < 531000))
test2 <- rbind(filter(noattacks, height >  610000 & height < 622000), 
               majority20) 

write.csv(t1,paste(local,'BTG_Train1_labeled.csv', sep=''))
write.csv(t2,paste(local,'BTG_Train2_labeled.csv', sep=''))
write.csv(t3,paste(local,'BTG_Train3_labeled.csv', sep=''))
write.csv(test1,paste(local,'BTG_Test1_labeled.csv', sep=''))
write.csv(test2,paste(local,'BTG_Test2_labeled.csv', sep=''))

ggplot(test1, aes(x=test1$height, y=test1$size)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$miner)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$confirmations)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$strippedsize)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$difficulty)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$nTx)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$num_out)) + geom_line()
ggplot(test1, aes(x=test1$height, y=last$num_in)) + geom_line()


