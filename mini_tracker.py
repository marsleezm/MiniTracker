from flask import Flask, jsonify, request
from flask_expects_json import expects_json
from flask_apscheduler import APScheduler

import logging
import requests
from myaddress import AddressMetadata 

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

address_dict = {} 

NOT_EXIST = 'The address does not exist.'
ALREADY_EXIST = 'The address already exists.'
NOT_SYNCHRONIZED = 'The address is not synchronized.'

@app.route('/')
def index():
    return "Welcome to MiniTracker", 200

@app.route("/address")
def get_address():
    res = []
    for address in address_dict.keys():
        res.append({"address": address})
    return jsonify(res)

@app.route("/address/<addr>", methods=['POST'])
def add_address(addr):
    if addr in address_dict:
        return ALREADY_EXIST, 400
    else:
        btc_addr = AddressMetadata(app.logger, addr)
        address_dict[addr] = btc_addr
        return 'Successfully added', 200

@app.route("/address/<addr>", methods=['DELETE'])
def delete_address(addr):
    if addr in address_dict:
        del address_dict[addr]
        return 'Successfully deleted', 200
    else:
        return NOT_EXIST, 404 

@app.route("/address/<addr>/txs", methods=['GET'])
def get_address_txs(addr):
    if addr not in address_dict:
        return NOT_EXIST, 404
    else:
        offset = request.args.get('offset', default = 0, type = int)
        limit = request.args.get('limit', default = 50, type = int)
        valid, res = address_dict[addr].get_txs(offset, limit) 
        if not valid:
            return NOT_SYNCHRONIZED, 500
        else:
            return jsonify(res) 

@app.route("/address/<addr>/balance", methods=['GET'])
def get_address_balance(addr):
    if addr not in address_dict:
        return NOT_EXIST, 400
    else:
        app.logger.info(address_dict[addr])
        valid, res = address_dict[addr].get_balance() 
        if not valid:
            return NOT_SYNCHRONIZED, 500
        else:
            return jsonify(res) 

def synchronize_txs():
    app.logger.info('********* Started syncing **********')
    for addr, btc_addr in address_dict.items():
        btc_addr.synchronize()
    app.logger.info('********* Finished syncing for %d addresses **********', len(address_dict))


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(id='synchronize_txs', func=synchronize_txs, trigger='interval', seconds=30)
    app.run(debug=True)
