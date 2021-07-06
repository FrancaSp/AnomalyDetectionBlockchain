from elasticsearch import Elasticsearch
import pandas as pd
from pandas.io.json import json_normalize
import time

class DataQuery():
    '''
    Class for potential Elasticsearch Queries on AnyBlocks Analytics (https://www.anyblockanalytics.com)
    '''
    http_auth = ('s9794755@stud.uni-frankfurt.de', 'a7212d89-fb73-42fa-bc45-b4227c5e5fc0')

    # Authentification on ANYblock Analytics API, in this case it stays the same
    def __init__(self, chain, where):
        '''
        The following class is the Data Query for the specific Network
        :param chain: list, Blockchain Network under analysis, list with two entries exp:['ethereum','classic']
        :param where: str, specification on what table the analysis should be made exp: 'block', 'tx'
        '''
        self.chain = chain
        self.where = where
        self.es = self._connect()
        
    def _connect(self):
        es = Elasticsearch(
            hosts=["https://api.anyblock.tools/" + self.chain[0] + "/" + self.chain[1] + "/mainnet/es/"],
            http_auth=DataQuery.http_auth, timeout=30, retry_on_timeout=True, max_retries=30)
        return es
    def collect_by(self, start, interval, range_by):#, features):
        '''
        Function to collect data by a specific time interval.
        :param start: start time, in unix format conversion can be made here https://www.unixtimestamp.com/index.php
        :param end: end time, in unix format conversion can be made here https://www.unixtimestamp.com/index.php
        :param range_by: stinrg, attribute to range the analysis by (normally 'timestamp')
        :return: dict from elasticsearch and converted DataFrame
        '''
        #es = Elasticsearch(
         #   base_endpoint=["https://api.anyblock.tools/" + self.chain[0] + "/" + self.chain[1] + "/mainnet/es/"],
          #  http_auth=DataQuery.http_auth, timeout=30, retry_on_timeout=True, max_retries=30)
        query = {
            'size': 10000,
            "query": {
                "range": {
                    range_by: {
                        "gte": start,
                        "lte": start+interval
                    }
                }
            },
            'sort':{"timestamp":'asc'}#,
            #"_source": {
                #"includes": features
                #}
        }
        res = self.es.search(
            index=self.chain[0] + "-" + self.chain[1] + "-mainnet" + "-" + self.where,
            body=query, scroll='2m')
        scrollId = res['_scroll_id']
        elastic_docs = res["hits"]["hits"]
        df = json_normalize(elastic_docs)
        return scrollId, df

    def collect_all(self):
        '''
        Function to start search with elastic and collect all data.
        :return: scrollID and DataFrame from collection
        '''
        es = Elasticsearch(
            hosts=["https://api.anyblock.tools/" + self.chain[0] + "/" + self.chain[1] + "/mainnet/es/"],
            http_auth=DataQuery.http_auth, timeout=30, retry_on_timeout=True, max_retries=30)
        query = {
            'size': 10000,  # free version of API calls is restricted to 120 calls per min
            'query': {
                'match_all': {}}}
        res = es.search(index=self.chain[0] + "-" + self.chain[1] + "-mainnet" + "-" + self.where,
                        body=query, scroll='2m')
        scrollId = res['_scroll_id']
        es_res = res["hits"]["hits"]
        df = json_normalize(es_res)
        return scrollId, df
    
    def get_block(self,blocknum, istx =True):
        '''
        :param blocknum: int, block number to get
        :param istx: bool, Traue if the tx should be included in the data
        :return:
        '''
        if istx:
            number = "blockNumber.num"
        else:
            number = 'number.num'
        query = {
                "size" : 5000,
                "query": {
                   #  "match_all" : {}
                    "match" : {
                        "blockNumber.num" : blocknum}
                        }
                    }
        res = self.es.search(index=self.chain[0] + "-" + self.chain[1] + "-mainnet" + "-" + self.where,
                            body=query)
        elastic_docs = res["hits"]["hits"]
        df = json_normalize(elastic_docs)
        return df

    def tx_parse(start, interval, df, counter = 0):
        '''
        :param interval: int, interval to parse the blocks
        :param df: pandas.DataFrame,
        :param counter: int, initially 0
        :return:pandas.Dataframe, df
        '''
        for idx in list(range(start, start + interval)):
            df1 = self.get_block(idx)
            df = df.append(df1)
            counter += 1
            print(counter)
        return df

    def scroll_data(self, scrollId, df, breaker, start, interval, range_by):
        '''
        The following function scrolls though elasticsearch in order to get more than 5000 entries.
        Needs the df from collect_all function.
        :param scrollId: ID for scroll, given by collect_all
        :param df: DataFrame that should be updated, given by collect_all
        :param breaker: counter to end recursive function
        :return: DataFrame with all scrolled data
        '''
        # es = Elasticsearch(
        #     hosts=["https://api.anyblock.tools/" + self.chain[0] + "/" + self.chain[1] + "/mainnet/es/"],
        #     http_auth=DataQuery.http_auth, timeout=30, retry_on_timeout=True, max_retries=30)
        #if breaker < 2:  # the API Calls are limited to 120 per hour
        try:
            res = self.es.scroll(scroll_id=scrollId, scroll='2m')
            es_res = res["hits"]["hits"]
            df1 = json_normalize(es_res)
            if len(df1) == 0:  # check if the job might be finished
                print('job finished')
                return df, scrollId 
            else:
                df = df.append(df1)
                scrollId = res['_scroll_id']
                breaker += 1
                print(breaker)
            return self.scroll_data(scrollId, df, breaker, start, interval, range_by)
        except:
            pass
#            print('Exception taken...')
#            return df, scrollId
#            start = start+(max(df['_source.'+range_by]) - min(df['_source.'+range_by]))
#            scrollId, df3 = ETC.collect_by(start, start+interval, range_by)
#            return self.scroll_data(scrollId, df3, breaker, start, interval, range_by)
        #else:
         #   print('job finished')
          #  return df, scrollId