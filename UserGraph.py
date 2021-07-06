import pandas as pd
import networkx as nx
import statistics

class DirectedGraph():
    '''
    Class for th ecreation of user/adress graphs.
    '''
    def __init__(self, df):
        self.df = df
        self.G = None
    def create_graph(self, var_from, var_to, metadata):
        '''
        :param var_from: string, name of feature that holds sending adress
        :param var_to: string, name of feature that holds recieving adress
        :param metadata: list, other data to pass as metadata
        :return:
        '''
        self.G = nx.from_pandas_edgelist(self.df, var_from, var_to, metadata, nx.DiGraph())
    def extract_variables(self):
        '''
        Function to iterate through the graph and extract values.
        :return: list of values and user dataframe
        '''
        lstin = []
        for u in self.G.nodes():
            in_etc = 0
            mean_in_etc = 0
            cum_gas_used = 0

            out_etc = 0
            mean_out_etc = 0.0
            cum_gas_price = 0
            cum_gas_limit = 0

            indegree = self.G.in_degree(u)
            outdegree = self.G.out_degree(u)
            avg_num_of_blocks_between_intx = 0
            avg_num_of_blocks_between_outtx = 0
            median_num_of_blocks_between_outtx = 0
            median_num_of_blocks_between_intx = 0
            numsenttx,avg_gas_limit, avg_gas_price = 0,0,0
            #avg_interval_in_tx_lst = []
            #avg_interval_out_tx_lst = []
            temp_blocklist = []
            for e1, e2, a in self.G.in_edges(u, data=True):
                in_etc = in_etc + float(a['value'])
                temp_blocklist.append(a['block_number'])
                try:
                    if a['label'] != 0:  # case of attack
                        label = 1
                    else:
                        label = 0
                except:
                    print('no label given, default set to 0')
                    label = 0
                #print(a['value'])
            #print(in_etc)
            if indegree != 0:
                mean_in_etc = in_etc / indegree
                temp_blocklist.sort()
                interval = [x1 - x2 for (x1, x2) in
                            zip(temp_blocklist[-(len(temp_blocklist) - 1):],
                                temp_blocklist[:(len(temp_blocklist) - 1)])]
                if len(interval) != 0:
                    avg_num_of_blocks_between_intx = sum(interval) / len(interval)#statistics.mean(interval)
                    median_num_of_blocks_between_intx = statistics.median(interval)
            noncelst = []
            temp_blocklist = []
            for e1, e2, a in self.G.out_edges(u, data=True):
                out_etc = out_etc + float(a['value'])
                cum_gas_used = cum_gas_used + float(a['gas_used'])
                cum_gas_price = cum_gas_price + float(a['gas_price'])
                cum_gas_limit = cum_gas_limit + float(a['gas'])
                temp_blocklist.append(a['block_number'])
                noncelst.append(a['nonce'])
                try:
                    if a['label'] != 0:  # case of attack
                        label = 1
                    else:
                        label = 0
                except:
                    print('no label given, default set to 0')
                    label = 0
            if len(noncelst) != 0:
                numsenttx = max(noncelst)
            if outdegree != 0:
                mean_out_etc = out_etc / outdegree
                mean_gas = cum_gas_used / outdegree
                avg_gas_price = cum_gas_price / outdegree
                avg_gas_limit = cum_gas_limit / outdegree
                temp_blocklist.sort()
                interval = [x1 - x2 for (x1, x2) in
                            zip(temp_blocklist[-(len(temp_blocklist) - 1):],
                                temp_blocklist[:(len(temp_blocklist) - 1)])]
                if len(interval) != 0:
                    avg_num_of_blocks_between_outtx = sum(interval) / len(interval)#statistics.mean(interval)
                    median_num_of_blocks_between_outtx = statistics.median(interval)
            lstin.append([u, in_etc, mean_in_etc, cum_gas_used, out_etc, mean_gas,
                          mean_out_etc, indegree, outdegree,
                          avg_num_of_blocks_between_intx,
                          avg_num_of_blocks_between_outtx,
                          median_num_of_blocks_between_outtx,
                          median_num_of_blocks_between_intx,
                          numsenttx, avg_gas_limit, avg_gas_price,
                          label
                          ])
        userdf = pd.DataFrame(lstin, columns= ['adress', 'in_etc', 'mean_in_etc', 'cum_gas_used', 'out_etc',
                              'mean_gas','mean_out_etc', 'indegree', 'outdegree','avg_num_of_blocks_between_intx',
                              'avg_num_of_blocks_between_outtx','median_num_of_blocks_between_outtx',
                              'median_num_of_blocks_between_intx','numsenttx', 'avg_gas_limit', 'avg_gas_price', 'label'])
        return lstin, userdf
