from datetime import datetime
from requests.adapters import HTTPAdapter, Retry
import requests
import logging
import time

URL = 'https://blockchain.info/rawaddr/{0}?offset={1}'
RETRIES = Retry(total=5, backoff_factor=3, status_forcelist=[429, 500, 502, 503, 504])
SLEEP_TIME = 5

class AddressMetadata:
    def __init__(self, logger, address):
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=RETRIES))

        self.logger = logger 
        self.address = address 
        # Transactions in timestamp ascending order. Therefore appending new txs is efficient.
        self.txs = []
        self.balance = None
        self.last_synced = None

    def synchronize(self):
        if self.txs:
            new_txs, balance = self.fetch_newer_txs(self.txs[-1]["time"])
        else:
            new_txs, balance = self.fetch_newer_txs(0)
        self.txs.extend(new_txs) 
        self.balance = balance
        self.last_synced = datetime.now()
        self.logger.info("Done syncing for %s, number of txs is %d, balance is %s", self.address, len(self.txs), self.balance)

    # fetch transactions with ts > timestamp
    def fetch_newer_txs(self, timestamp):
        r = self.delayed_get(URL.format(self.address, len(self.txs)))
        if r.status_code != 200:
            raise Exception("Can not finish the request, status code was %d", r.status_code)

        tmp_txs = r.json()['txs']
        offset = len(tmp_txs)
        balance = r.json()['final_balance'] 

        txs_buffer = []

        while len(tmp_txs) and timestamp < tmp_txs[-1]["time"]:
            txs_buffer.extend(tmp_txs)
            offset, tmp_txs, balance = self.fetch_older_txs(tmp_txs[-1]["time"], offset)

        txs = self.get_newer_txs(tmp_txs, timestamp)
        txs_buffer.extend(txs)

        return txs_buffer[::-1], balance

    def get_newer_txs(self, txs, timestamp):
        if timestamp == 0 or not txs:
            return txs

        idx = len(txs) - 1 
        while idx >= 0 and txs[idx]['time'] != timestamp: 
            idx -= 1
        if idx == -1:
            raise Exception("Wanted to find all transactions before %d, but some transactions are missing", timestamp)
        else:
            return tmp_txs[:idx]

    # fetch transactions with ts < timestamp
    def fetch_older_txs(self, timestamp, offset):
        r = self.delayed_get(URL.format(self.address, offset))
        if r.status_code == 200:
            tmp_txs = r.json()['txs']
            balance = r.json()['final_balance'] 

            idx = 0
            while idx < len(tmp_txs) and timestamp >= tmp_txs[idx]["time"]:
                r = self.delayed_get(URL.format(self.address, offset))
                if r.status_code != 200:
                    raise Exception("Can not finish the request, status code was %d", r.status_code)
                tmp_txs = r.json()['txs']
                balance = r.json()['final_balance'] 
                idx += 1

            return offset + len(tmp_txs), tmp_txs[idx:], balance
        else:
            raise Exception("Can not finish the request, status code was %d", r.status_code)

    def get_balance(self):
        if self.last_synced == None:
            return False, {}
        else:
            return True, {"balance": self.balance, "synchronized_time": self.last_synced }

    def get_txs(self, offset, limit):
        if self.last_synced == None:
            return False, {}
        else:
            txs = self.txs[offset:offset+limit]
            return True, {"transactions": txs, "synchronized_time": self.last_synced }

    def delayed_get(self, url):
        time.sleep(SLEEP_TIME)
        return self.session.get(url)
