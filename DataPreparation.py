import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import ast
import requests

class DataPreparation():
    def __init__(self, df, timestep):
        '''
        :param df: Data Frame. to prepare
        :param timestep: int, number of timesteps for lstm
        '''
        self.df = df
        self.timestep = timestep
    def change_idx(self):
        '''
        :return: pandas.DataFrame
        '''
        self.df = self.df.sort_values('number')
        self.df = self.df.set_index(pd.Index(list(range(1, len(self.df) + 1))))
        return self.df

    def drop_first_n_cols(self):
        '''
        :return: pandas.DataFrame
        '''
        self.df.drop(self.df.head(len(self.df)%self.timestep).index, inplace=True)#
        return self.df

    def add_num_empty_blocks(self):
        '''
        :return: pandas.DataFrame, with new column for empty blocks
        '''
        self.df['num_emptyblocks'] = pd.Series([0] * len(self.df), index=self.df.index)
        counter = 0
        for idx in list(self.df.index):
            try:
                if str(self.df.at[idx - 1, 'num_tx']) != 'nan':
                    counter = 0
                else:
                    counter += 1
            except:
                pass
            try:
                self.df.at[idx, 'num_emptyblocks'] = counter
            except:
                pass
        self.df = self.df.fillna(0)
        return self.df

    def add_miner_dummy(self):
        '''
        :return: pandas.DataFrame, with new column for dummy miner
        '''
        self.df['dummy_miner_before'] = pd.Series([0] * len(self.df), index=self.df.index)
        for idx in list(self.df.index):
            try:
                if self.df.at[idx - 1, 'miner'] == self.df.at[idx, 'miner']:
                    self.df.at[idx, 'dummy_miner_before'] = 1
            except:
                print('Exception for Lists first Datapoint')
        return self.df
    def add_miner_count(self):
        '''
        :return: pandas.DataFrame, with new column for miner count
        '''
        self.df['dummy_miner_count'] = pd.Series([0] * len(self.df), index=self.df.index)
        counter = 0
        for idx in list(self.df.index):
            try:
                if self.df.at[idx - 1, 'dummy_miner_before'] == 0:
                    counter = 0
                else:
                    counter += 1
            except:
                pass
            self.df.at[idx, 'dummy_miner_count'] = counter
        return self.df
    def add_uncle_info(self,uncle_df,num_uncles = 0,total_num_uncles=409375):
        '''
        :param uncle_df: pandas.DataFrame, with uncle data
        :param num_uncles: int, count for num
        :param total_num_uncles: int, starting number of total_num_uncles count
        :return:
        '''
        self.df = self.df.set_index(self.df['number'])
        # block = block.sort_values(['number'])
        self.df['num_uncles'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['total_num_uncles'] = pd.Series([0] * len(self.df), index=self.df.index)
        for idx in list(self.df['number']):
            if idx in list(uncle_df['number']):
                num_uncles += 1
                total_num_uncles += 1
                self.df.at[idx, 'num_uncles'] = num_uncles
                self.df.at[idx, 'total_num_uncles'] = total_num_uncles
            else:
                num_uncles = 0
                self.df.at[idx, 'total_num_uncles'] = total_num_uncles
        self.change_idx()
        return self.df

    def change_data_types(self, cols):
        '''
        :param cols: list, names of cols that are relevatn for analysis
        :return:
        '''
        for idx in list(self.df.index):
            try:
                self.df.at[idx, 'extra_data'] = int(str(self.df['extra_data'][idx]), base=36)
                self.df.at[idx, 'miner'] = int(str(self.df['miner'][idx]), base=36)
            except:
                pass
        self.df = self.df.astype({'extra_data': 'float64', 'total_difficulty': 'float',
                                  'miner': 'float', 'num_tx': 'int64', 'avg_tx_value': 'float',
                                  'avg_nonce': 'float', 'size': 'int64', 'gas_used': 'int64',
                                  'gas_limit': 'int64', 'num_uncles': 'int64', 'total_num_uncles': 'int64',
                                  'difficulty': 'float'})
        #self.df = self.df.drop(columns=cols)
        self.df = self.df.loc[:,cols]
        return self.df

    def scale(self):
        '''
        :return: pandas.DataFrame, scaled
        '''
        scaler = MinMaxScaler(feature_range=(0, 1))
        df1 = scaler.fit_transform(self.df)
        return df1
    def transform_data(self):
        '''
        :return: numpy.array, containing sliding window data in format (observations, timestep, features)
        '''
        #self.df = self.df.fillna(0)
        #self.df = self.df.replace(np.nan, 0)
        df1 = self.scale()
        # Store window number of points as a sequence
        xin = []
        # next_X = []
        for i in range(self.timestep, len(df1)):
            xin.append(df1[i - self.timestep:i])
            # next_X.append(df1[i])
        # Reshape data to format for LSTM
        xin = np.array(xin)  # , np.array(next_X)
        # old df1 = np.reshape(df1, (int(len(self.df) / self.timestep), self.timestep, len(self.df.columns)))
        return xin
    def get_hashrate(self):
        '''
        :return: pandas.DataFrame, combine the Data from API about hashrate and block_time with block data
        '''
        r = requests.get('https://hr.2miners.com/api/v1/hashrate/1d/etc')
        df = pd.DataFrame.from_dict(r.json())
        relevant = df[(df['timestamp'] <= max(self.df['time'])) & (df['timestamp'] >= min(self.df['time']))]
        self.df['hashrate'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['block_time'] = pd.Series([0] * len(self.df), index=self.df.index)
        for index,row in relevant.iterrows():
            try:
                end = relevant.timestamp[index]
                start = relevant.timestamp[index+1]
                temp = self.df[self.df['time'].between(start, end-1)]
                self.df.loc[temp.index, 'hashrate'] = relevant.hashrate[index]
                self.df.loc[temp.index, 'block_time'] = relevant.block_time[index]
            except:
                pass
        # taking care of upper bound
        temp = self.df[self.df['time'].between(max(relevant.timestamp), max(self.df.time))]
        self.df.loc[temp.index, 'hashrate'] = int(relevant.loc[relevant.timestamp==max(relevant.timestamp)].hashrate)
        self.df.loc[temp.index, 'block_time'] = int(relevant.loc[relevant.timestamp==max(relevant.timestamp)].block_time)
        # taking care of lower bound
        temp = self.df[self.df['time'].between(min(self.df.time), min(relevant.timestamp))]
        self.df.loc[temp.index, 'hashrate'] = int(relevant.loc[relevant.timestamp==min(relevant.timestamp)].hashrate)
        self.df.loc[temp.index, 'block_time'] = int(relevant.loc[relevant.timestamp==min(relevant.timestamp)].block_time)
        return self.df
    def num_features(self):
        '''
        :return: return number of features of the Data Frame
        '''
        return print('The Number of Features of our Data Frame is: ' + str(len(self.df.index)))
class BTGDataPrep():
    '''
    Extra Class for Data Preparation for Bitcoin Gold
    '''
    def __init__(self,df,timestep):
        '''
        :param df: pandas.DataFrame, to prepare
        :param timestep: int, timestep to look back to
        '''
        self.df = df
        self.timestep = timestep
    def initialize_new_vars(self):
        '''
        :return: pandas.DataFrame, initializing data to parse from tx
        '''
        self.df['miner'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['total_reward'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['num_in'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['num_out'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['btg_out'] = pd.Series([0] * len(self.df), index=self.df.index)
        return self.df

    def parse_variables(self):
        '''
        :return: pandas.DataFrame, parse the data from tx
        '''
        self.initialize_new_vars()
        for block in list(self.df.index):  #iterate through blocks
            tx = self.df.loc[block].tx
            tx = ast.literal_eval(tx)
            num_inputs = 0
            num_outputs = 0
            out_btg = 0
            if len(tx[0]['vout']) <= 2:
                if tx[0]['vout'][0]['scriptPubKey']['type'] == 'nulldata':
                    # check if the nulldata is in first place
                    self.df.loc[block, 'miner'] = tx[0]['vout'][1]['scriptPubKey']['addresses'][0]
                    self.df.loc[block, 'total_reward'] = tx[0]['vout'][1]['value']
                else:
                    self.df.loc[block, 'miner'] = tx[0]['vout'][0]['scriptPubKey']['addresses'][0]
                    self.df.loc[block, 'total_reward'] = tx[0]['vout'][0]['value']
            else:
                tot_rew = 0
                lst_miners = []
                for out in list(range(0, len(tx[0]['vout'])-1)):
                    tot_rew += tx[0]['vout'][out]['value']
                    if tx[0]['vout'][out]['scriptPubKey']['type'] != 'nulldata':
                        lst_miners.append(tx[0]['vout'][out]['scriptPubKey']['addresses'][0])
                self.df.loc[block, 'total_reward'] = tot_rew
                self.df.loc[block, 'miner'] = str(lst_miners)
            try:
                for itx in list(range(1, len(tx))):  # iterate through transactions
                    num_inputs += len(tx[itx]['vin'])
                    num_outputs += len(tx[itx]['vout'])
                    for out in list(range(0, len(tx[itx]['vout']))):  #iterate throgh outputs of txs
                        out_btg += tx[itx]['vout'][out]['value']
            except:
                print('Coinbase Transaction only')
            self.df.loc[block, 'num_in'] = num_inputs
            self.df.loc[block, 'num_out'] = num_outputs
            self.df.loc[block, 'btg_out'] = out_btg
        return self.df
    def drop_cols(self):
        '''
        :return: pandas.DataFrame, filter for cols
        '''
        #self.df.drop(self.df.head(len(self.df) % self.timestep).index, inplace=True)  #
        cols = ['height', 'confirmations', 'strippedsize','difficulty',
                'size', 'weight','time', 'mediantime','nTx','miner',
                'total_reward', 'num_in', 'num_out', 'btg_out', 'hashrate',
                'block_time']
        self.df = self.df.loc[:, cols]
        return self.df

    def get_hashrate(self):
        '''
        :return: pandas.DataFrame, combine the Data from API about hashrate and block_time with block data
        '''
        r = requests.get('https://hr.2miners.com/api/v1/hashrate/1d/btg')
        df = pd.DataFrame.from_dict(r.json())
        relevant = df[(df['timestamp'] <= max(self.df['time'])) & (df['timestamp'] >= min(self.df['time']))]
        self.df['hashrate'] = pd.Series([0] * len(self.df), index=self.df.index)
        self.df['block_time'] = pd.Series([0] * len(self.df), index=self.df.index)
        for index,row in relevant.iterrows():
            try:
                end = relevant.timestamp[index]
                start = relevant.timestamp[index+1]
                temp = self.df[self.df['time'].between(start, end-1)]
                self.df.loc[temp.index, 'hashrate'] = relevant.hashrate[index]
                self.df.loc[temp.index, 'block_time'] = relevant.block_time[index]
            except:
                pass
        # taking care of upper bound
        temp = self.df[self.df['time'].between(max(relevant.timestamp), max(self.df.time))]
        self.df.loc[temp.index, 'hashrate'] = int(relevant.loc[relevant.timestamp==max(relevant.timestamp)].hashrate)
        self.df.loc[temp.index, 'block_time'] = int(relevant.loc[relevant.timestamp==max(relevant.timestamp)].block_time)
        # taking care of lower bound
        temp = self.df[self.df['time'].between(min(self.df.time), min(relevant.timestamp))]
        self.df.loc[temp.index, 'hashrate'] = int(relevant.loc[relevant.timestamp==min(relevant.timestamp)].hashrate)
        self.df.loc[temp.index, 'block_time'] = int(relevant.loc[relevant.timestamp==min(relevant.timestamp)].block_time)
        return self.df
    def add_miner_dummy(self):
        '''
        :return: pandas.DataFrame, with new column for dummy miner
        '''
        self.df['dummy_miner_before'] = pd.Series([0] * len(self.df), index=self.df.index)
        for idx in list(self.df.index):
            try:
                if self.df.at[idx - 1, 'miner'] == self.df.at[idx, 'miner']:
                    self.df.at[idx, 'dummy_miner_before'] = 1
            except:
                print('Exception for Lists first Datapoint')
        return self.df
    def add_miner_count(self):
        '''
        :return: pandas.DataFrame, with new column for miner count
        '''
        self.df['dummy_miner_count'] = pd.Series([0] * len(self.df), index=self.df.index)
        counter = 0
        for idx in list(self.df.index):
            try:
                if self.df.at[idx - 1, 'dummy_miner_before'] == 0:
                    counter = 0
                else:
                    counter += 1
            except:
                pass
                self.df.at[idx, 'dummy_miner_count'] = counter
        return self.df