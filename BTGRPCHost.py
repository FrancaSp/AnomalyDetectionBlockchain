from __future__ import print_function
import time, requests, json
from pandas.io.json import json_normalize
import pandas as pd
import ast 

class RPCHost(object):
    '''
    Fork from https://gist.github.com/Deadlyelder/6baad86e832acf0df23a70914c014d7a#file-bitcoin_rpc_class-py
    '''
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}
    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadFailedConnections = True
                print("Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} more tries)".format(tries))
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']

class RPCScrollBTC(RPCHost):
    '''
    This class is used to parse Bitcoin Data from the RPC API of AnyBlocks Analytics (https://www.anyblockanalytics.com)
    Since within the Thesis I decided to only work with Bitcoin Gold and Ethereum Classic Data, the class
    wasn't needed for the reasearch question.
    '''
    url = 'https://api.anyblock.tools/bitcoin/bitcoin/mainnet/rpc/a7212d89-fb73-42fa-bc45-b4227c5e5fc0/'
    def __init__(self, interval):
        '''
        :param interval: int, number of blocks to get from RPC Call
        '''
        self.interval = interval
        self.host = RPCHost(RPCScrollBTC.url)
    def getblock(self,start_idx):
        '''
        :param start_idx: int, block number to start with
        :return: pandas.DataFrame, with blocks starting from start_idx ending with start_idx+interval
        '''
        blockhash = self.host.call('getblockhash', start_idx)
        print('Initial Block of Scroll..' + blockhash)
        block = self.host.call('getblock', blockhash) #, 2)
        df = json_normalize(block)  # we need this df to append rows of loop
        for idx in list(range(start_idx + 1, start_idx + self.interval)):
            try:
                blockhash = self.host.call('getblockhash', idx)
                block = self.host.call('getblock', blockhash) #, 2)
                df2 = json_normalize(block)
                df = df.append(df2)
            except:
                print('Exception taken')
                pass
        df = df.reset_index(drop=True)
        print(len(df))
        print(df.head)
        return df

class RPCScrollBTG(RPCHost):
    '''
    Class to make RPC Calls on the full Node I setup for Bitcoin Gold.
    If the class should be used to connect to another full Node the Credentaials need to be adjusted.
    '''
    rpcPort = 8332
    rpcUser = 'franca'
    rpcPassword = 'masterthesis2021'
    serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@localhost:' + str(rpcPort)
    def __init__(self, interval):
        '''
        :param interval: int, number of blocks to get from RPC Call
        '''
        self.interval = interval
        self.host = RPCHost(RPCScrollBTG.serverURL)
    def getblock(self, start_idx):
        '''
        :param start_idx: int, block number to start with
        :return: pandas.DataFrame, with blocks starting from start_idx ending with start_idx+interval
        '''
        blockhash = self.host.call('getblockhash', start_idx)
        print('Initial Block of Scroll..' + blockhash)
        block = self.host.call('getblock', blockhash, 2)
        df = json_normalize(block) # we need this df to append rows of loop
        for idx in list(range(start_idx+1,start_idx+self.interval)):
            try:
                blockhash = self.host.call('getblockhash', idx)
                block = self.host.call('getblock', blockhash, 2)
                df2 = json_normalize(block)
                df = df.append(df2)
            except: # deals with out of index errors 
                #return(df)
                break
        df=df.reset_index(drop = True)
        tx = df['tx'][0]
       # print(tx)
        print(type(tx))
        print(len(tx))
        print(df.index)
        #tx = ast.literal_eval(tx)
        txdf = json_normalize(tx)
        for i in list(range(1,len(df))):
            tx = df['tx'][i]
            #tx = ast.literal_eval(tx)
            txdf1 = json_normalize(tx)
            txdf = txdf.append(txdf1)
        print('Iterator: ' + str(i) + 'Index: ' + str(idx))
        print(len(df))
        print(df.head)
        return df, txdf

class TxParser():
    '''
    Class to parse the Transaction Data from our Block Data we collected via RPC.
    '''
    def __init__(self, directory):
        '''
        :param directory: string, path to your data dir
        '''
        self.directory = directory
    def parse(self):
        '''
        :return: pandas.DataFrame, containing the Transaction Data
        '''
        df = pd.read_csv(self.directory)
        tx = df['tx'][0]
        tx = ast.literal_eval(tx)
        df1 = json_normalize(tx)
        for idxtx in list(range(1,len(df))):
            tx = df['tx'][idxtx]
            tx = ast.literal_eval(tx)
            df2 = json_normalize(tx)
            df1 = df1.append(df2)
        return(df1)


