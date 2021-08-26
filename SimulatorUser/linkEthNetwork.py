import json
from web3 import Web3, HTTPProvider
from web3.contract import Contract


class systemControling(object):

    def __init__(self, address,abiPath,host, account):
        self.contractAddress = address
        self.web3 = Web3(HTTPProvider(host))
        self.account = account
        
        abiFile = open(abiPath)
        abi = json.load(abiFile)
        abiFile.close()
        self.contract_inst = self.web3.eth.contract(abi=abi,address=self.contractAddress)
        self.blockNumber = self.web3.eth.blockNumber
        self.gas=400000

    def getUserIndex(self):
        return self.contract_inst.functions.getUserIndex().call({'from': self.web3.eth.accounts[self.account]})

    def getIfSystemNeedEnergy(self):
        return self.contract_inst.functions.getIfSystemNeedEnergy().call({'from': self.web3.eth.accounts[self.account]})

    def getSystemRuning(self):
        return self.contract_inst.functions.sysRunSta().call({'from': self.web3.eth.accounts[self.account]})

    def getUserDataPower(self):
        return self.contract_inst.functions.getUserDataPower().call({'from': self.web3.eth.accounts[self.account]})

    def getTestNumber(self):
        return self.contract_inst.functions.getTestNumber().call({'from': self.web3.eth.accounts[self.account]})

    def setUserDataPower(self,P):
        self.contract_inst.functions.setUserDataPower(P).transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas})

    def autoRegistrationNewUser(self):
        self.contract_inst.functions.autoRegistrationNewUser().transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas})

    def modifaySystemTarifeNumber(self,TarNum):
        self.contract_inst.functions.modifaySystemTarifeNumber(TarNum).transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas})

    def checkBlock(self):
        if self.web3.eth.blockNumber==self.blockNumber:
            return False
        else:
            self.blockNumber=self.web3.eth.blockNumber
            return True

    def getBlock(self):
        return self.blockNumber



class electricityBilling(object):
    
    def __init__(self, address,abiPath,host, account):
        self.contractAddress = address
        self.web3 = Web3(HTTPProvider(host))
        self.account = account
        
        abiFile = open(abiPath)
        abi = json.load(abiFile)
        abiFile.close()
        self.contract_inst = self.web3.eth.contract(abi=abi,address=self.contractAddress)
        self.blockNumber = self.web3.eth.blockNumber
        self.gas=200000

    def getUserIndex(self):
        return self.contract_inst.functions.getUserIndex().call({'from': self.web3.eth.accounts[self.account]})

    def getUserWalletInCent(self):
        return self.contract_inst.functions.getUserWalletInCent().call({'from': self.web3.eth.accounts[self.account]})

    def getUserFinalEnergyPriceInCent(self):
        return self.contract_inst.functions.getUserFinalEnergyPriceInCent().call({'from': self.web3.eth.accounts[self.account]})

    def modifaySystemTarifPrice(self,TarNum,PriceBuy,priceSell):
        self.contract_inst.functions.modifaySystemTarifPrice(TarNum,PriceBuy,priceSell).transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas})

    def autoRegistrationNewUser(self):
        self.contract_inst.functions.autoRegistrationNewUser().transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas})

    def setUserDataEnergy(self,E):
        self.contract_inst.functions.setUserDataEnergy(E).transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas})

    def processingBillingForEnergy(self):
        self.contract_inst.functions.processBillingForEnergy().transact({'from': self.web3.eth.accounts[self.account], 'gas': self.gas*5})

