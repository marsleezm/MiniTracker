from flask import Flask, jsonify, request
from flask_expects_json import expects_json
from flask_apscheduler import APScheduler
import logging
import requests
from .myaddress import Address

app = Flask(__name__)

schema = {
  "type": "object",
  "properties": {
    "id": { "type": "string" },
  },
  "required": ["id"]
}

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

address_dict = {} 

@app.route("/address")
def get_address():
    res = []
    for address in address_dict.keys():
        res.append({"id": address})
    return jsonify(res)

@app.route("/address", methods=['POST'])
@expects_json(schema)
def add_address():
    addr = request.get_json()['id']
    app.logger.info('%s output address', addr)
    btc_addr = Address(app.logger, addr)
    address_dict[addr] = btc_addr
    return '', 204

@app.route("/address", methods=['DELETE'])
@expects_json(schema)
def delete_address():
    addr = request.get_json()['id']
    if addr in address:
        del address_dict[addr]
    return '', 204

@app.route("/address/<addr>/tx", methods=['GET'])
def get_address_txs(addr):
    if addr not in address_dict:
        return 'Address was not previously added', 400
    else:
        valid, res = address_dict[addr].txs() 
        if valid:
            return 'address not synchronized yet', 500
        else:
            return jsonify(res) 

@app.route("/address/<addr>/balance", methods=['GET'])
def get_address_balance(addr):
    if addr not in address_dict:
        return 'Address was not previously added', 400
    else:
        valid, res = address_dict[addr].balance() 
        if valid:
            return 'address not synchronized yet', 500
        else:
            return jsonify(res) 

def synchronize_txs():
    app.logger.info('********* Started syncing **********')
    for addr, btc_addr in address_dict.items():
        btc_addr.synchronize()
    app.logger.info('********* Finished syncing for %d addresses **********', len(address_dict))

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scheduler.add_job(id='synchronize_txs', func=synchronize_txs, trigger='interval', seconds=10)
