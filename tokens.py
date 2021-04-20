import json, requests
from config import web3
from config import BscScan_key

def get_abi(address):
    api_link = f'https://api.bscscan.com/api?module=contract&action=getabi&address={address}&apikey={BscScan_key}'
    api_link_dump = (requests.get(api_link)).json()
    abi = api_link_dump.get('result')
    return json.loads(abi)


class pair:
    def __init__(self,name):
        self.name = name.upper()

    def createContract(self,address):   
        addie = web3.toChecksumAddress(address)
        json_abi = get_abi(addie)
        contract = web3.eth.contract(address= addie, abi= json_abi)
        return contract

class token:
    def __init__(self,name):
        self.name = name.upper()

    def createContract(self,address):   
        addie = web3.toChecksumAddress(address)
        json_abi = get_abi(addie)
        contract = web3.eth.contract(address= addie, abi= json_abi)
        return contract