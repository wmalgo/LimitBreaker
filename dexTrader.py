import logging, time

class DexTrader:
    def __init__(self,exchange,web3_providor):
        self.client = exchange
        self.w3 = web3_providor
        self.account = self.client.account

    def AmountSlippage(self,pair_contract,slippage):
        first_token = self.w3.toChecksumAddress(pair_contract.functions.token0().call())
        if first_token == self.client.currency:
            reserves = pair_contract.functions.getReserves().call()
            shitcoin = float(self.w3.fromWei(reserves[1], 'ether'))
            limit = (0.01 * shitcoin) / (1 - (slippage/100))
            return self.w3.toWei(limit, 'ether')
        else:
            reserves = pair_contract.functions.getReserves().call()
            shitcoin = float(self.w3.fromWei(reserves[0], 'ether'))
            limit = (0.01 * shitcoin) / (1 - (slippage/100))
            return self.w3.toWei(limit, 'ether')

    def getTokenBalance(self,token_contract):
        balance = token_contract.functions.balanceOf(self.account).call()
        return balance

    def getPath(self,pair_contract, mode):
        token0 = self.w3.toChecksumAddress(pair_contract.functions.token0().call())
        token1 = self.w3.toChecksumAddress(pair_contract.functions.token1().call())
        if mode == 'buy':
            if token0 == self.client.currency:    
                path = [token0,token1]
            else:
                path = [token1,token0]
        elif mode == 'sell':
            if token0 == self.client.currency:    
                path = [token1,token0]
            else:
                path = [token0,token1]
        return path

    def getBalance(self):
        balance = self.w3.eth.getBalance(self.account)
        gas_money = self.w3.toWei(0.1,'ether')
        return balance - gas_money

    def getTradeAmount(self):
        balance = self.getBalance()
        lowest_amount_allowed = self.w3.toWei(2.5,'ether')
        if balance >= lowest_amount_allowed:
            return balance
        else:
            return None

    def tx_isValid(self,tx_hash):
        hex_hash = self.w3.toHex(tx_hash)
        while True:
            try:
                receipt = self.w3.eth.getTransactionReceipt(hex_hash)
                receipt_dict = dict(receipt)
                status = receipt_dict.get('status')
                break
            except:
                time.sleep(10)
        if status == 1:
            return True
        else:
            return False

    def buy(self,pair_contract,price,time):
        rsi_value = round(price)
        logging.info('BUY: {} at {} RSI'.format(pair_contract,rsi_value))
        buy_amount = self.getTradeAmount()
        if buy_amount <= self.AmountSlippage(pair_contract,20) and buy_amount != None:
            amount = buy_amount
        else:
            return False
        amountl = int(amount/price)
        amountmin = amountl - (int(amountl * 0.03))
        path = self.getPath(pair_contract, 'buy')
        tx_hash = self.client.swapExactETHForTokens(amount,amountmin,path)
        time.sleep(10)
        validity = tx_hash(self.tx_isValid(tx_hash))
        if validity == True:
            return True
        else:
            return False
        return True
        
    def sell(self,token_contract,price,time):
        if self.client.isApproved(token_contract) == False:
            self.client.approve(token_contract)
            time.sleep(10)
        amount = self.getTokenBalance(token_contract)
        amount_min = int(price * (amount - (amount * 0.05)))
        path = self.getPath(token_contract,'sell')
        tx_hash = self.client.swapExactTokensForETH(amount,amount_min,path)
        return tx_hash
    
    def closePositions(self):
        return