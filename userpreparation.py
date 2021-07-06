from UserGraph import DirectedGraph
import pandas as pd
import numpy as np

tx1 = pd.read_csv('/Volumes/Thesis/BlockchainData/ETC/ETC_tx_2018_reduced.csv')
tx2 = pd.read_csv('/Volumes/Thesis/BlockchainData/ETC/ETC_tx_2019_reduced.csv')
tx3 = pd.read_csv('/Volumes/Thesis/BlockchainData/ETC/ETC_tx_2020_reduced.csv')
txall = pd.concat([tx1,tx2,tx3], ignore_index= True)
metadata = ['gas', 'gas_price','nonce', 'value', 'gas_used', 'block_number']
var_from = 'from'
var_to = 'to'

g3 = DirectedGraph(tx3)
lstin, userdf  =g3.create_graph(var_from,var_to,metadata)