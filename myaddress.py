from datetime import datetime
from requests.adapters import HTTPAdapter, Retry
import requests
import logging

url = 'https://blockchain.info/rawaddr/{0}?offset={1}'
retries = Retry(total=5, backoff_factor=3, status_forcelist=[429, 500, 502, 503, 504])

class Address:
    def __init__(self, logger, address):
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

        self.logger = logger 
        self.address = address 
        # Transactions in timestamp ascending order. Therefore appending new txs is efficient.
        self.txs = []
        self.balance = None
        self.last_synced = None

    def synchronize(self):
        if self.txs != []:
            new_txs, balance = self.get_newer_txs(self.txs[-1]["time"])
            self.txs.extend(new_txs) 
            self.balance = balance
            self.last_synced = datetime.now()
            self.logger.info("Done syncing for %s, number of txs is %d, balance is %s", self.addr, len(self.txs), self.balance)
        else:
            self.init_synchronize()

    def get_newer_txs(self, timestamp):
        r = self.session.get(url.format(self.address, 0))
        if r.status_code != 200:
            raise Exception("Can not finish the request, status code was %d", r.status_code)

        tmp_txs = r.json()['txs']
        balance = r.json()['final_balance'] 

        txs_buffer = []

        while timestamp < tmp_txs[-1]["time"]:
            txs_buffer.extend(tmp_txs)
            tmp_txs, balance = sefl.get_older_txs(tmp_txs[-1]["time"], len(txs_buffer))

        idx = len(tmp_txs) - 1 
        while idx >= 0 and tmp_txs[idx] != timestamp: 
            idx -= 1
        if idx == -1:
            raise Exception("Wanted to find all transactions before %d, but some transactions are missing", timestamp)
        else:
            txs_buffer.extend(tmp_txs[:idx])

        return txs_buffer[::-1], balance

    def get_older_txs(self, timestamp, offset):
        backoff = 1
        offset -= backoff
        r = self.session.get(url.format(self.address, offset))
        if r.status_code == 200:
            tmp_txs = r.json()['txs']
            balance = r.json()['final_balance'] 

            while timestamp < tmp_txs[0]["time"]:
                offset -= backoff
                r = self.session.get(url.format(self.address, offset))
                if r.status_code != 200:
                    raise Exception("Can not finish the request, status code was %d", r.status_code)
                tmp_txs = r.json()['txs']
                balance = r.json()['final_balance'] 

            return tmp_txs[1:], balance
        else:
            raise Exception("Can not finish the request, status code was %d", r.status_code)

    def init_synchronize(self):
        r = self.session.get(url.format(self.address, 0))
        if r.status_code == 200:
            resp = r.json()
            self.balance = resp['final_balance']
            self.txs = resp['txs'] 
            if self.txs == []:
                return 

            tmp_txs, self.balance = self.get_older_txs(self.txs[-1]["time"], len(self.txs))
            while len(tmp_txs) > 0:
                self.txs.extend(tmp_txs)
                tmp_txs, self.balance = self.get_older_txs(self.txs[-1]["time"], len(self.txs))

            self.txs = self.txs[::-1] 
            self.last_synced = datetime.now()
            self.logger.info("Finished initial syncing for %s, number of txs is %d, balance is %s", self.addr, len(self.txs), self.balance)
        else:
            raise Exception("Can not finish the request, status code was %d", r.status_code)

    def balance(self):
        if self.last_synced == None:
            return false, {}
        else:
            return {"balance": self.balance, "synchronized_time": self.last_synced }

    def txs(self):
        if self.last_synced == None:
            return false, {}
        else:
            return true, {"balance": self.balance, "synchronized_time": self.last_synced }
