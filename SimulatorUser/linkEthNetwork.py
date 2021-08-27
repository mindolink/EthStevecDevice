import json
from web3 import Web3, HTTPProvider
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.middleware import local_filter_middleware
from web3.middleware import construct_sign_and_send_raw_middleware


class systemControling(object):

    def __init__(self, address,abiPath,host):
        self.contractAddress = address
        self.web3 = Web3(HTTPProvider(host))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.userAccount=self.web3.eth.coinbase
        self.blockNumber = self.web3.eth.blockNumber
        self.gas=400000

        abiFile = open(abiPath)
        abi = json.load(abiFile)
        abiFile.close()
        self.contract_inst = self.web3.eth.contract(abi=abi,address=self.contractAddress)

    def getUserIndex(self):
        return self.contract_inst.functions.getUserIndex().call({'from':self.userAccount})

    def autoRegistrationNewUser(self):
        self.contract_inst.functions.autoRegistrationNewUser().transact({'from':self.userAccount,'gas':self.gas})

    def getSystemNeedEnergy(self):
        return self.contract_inst.functions.getIfSystemNeedEnergy().call({'from':self.userAccount})

    def getSystemRun(self):
        return self.contract_inst.functions.sysRunSta().call({'from':self.userAccount})

    def getUserDataPower(self):
        return self.contract_inst.functions.getUserDataPower().call({'from':self.userAccount})

    def getTestNumber(self):
        return self.contract_inst.functions.getTestNumber().call({'from':self.userAccount})

    def setUserDataPower(self,P):
        self.contract_inst.functions.setUserDataPower(P).transact({'from':self.userAccount,'gas':self.gas})

    def modifaySystemTarifeNumber(self,TarNum):
        self.contract_inst.functions.modifaySystemTarifeNumber(TarNum).transact({'from':self.userAccount ,'gas':self.gas})

    def checkBlock(self):
        if (self.web3.eth.blockNumber==self.blockNumber):
            return False
        else:
            self.blockNumber=self.web3.eth.blockNumber
            return True

    def getBlock(self):
        return self.blockNumber


class electricityBilling(object):
    
    def __init__(self, address,abiPath,host):

        self.contractAddress = address
        self.web3 = Web3(HTTPProvider(host))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.userAccount=self.web3.eth.coinbase
        self.blockNumber = self.web3.eth.blockNumber
        self.gas=400000

        abiFile = open(abiPath)
        abi = json.load(abiFile)
        abiFile.close()
        self.contract_inst = self.web3.eth.contract(abi=abi,address=self.contractAddress)


    def getUserIndex(self):
        return self.contract_inst.functions.getUserIndex().call({'from':self.userAccount })

    def autoRegistrationNewUser(self):
        self.contract_inst.functions.autoRegistrationNewUser().transact({'from':self.userAccount,'gas':self.gas})

    def getUserWalletInCent(self):
        return self.contract_inst.functions.getUserWalletInCent().call({'from':self.userAccount})

    def getUserFinalEnergyPriceInCent(self):
        return self.contract_inst.functions.getUserFinalEnergyPriceInCent().call({'from':self.userAccount})

    def modifaySystemTarifPrice(self,TarNum,PriceBuy,priceSell):
        self.contract_inst.functions.modifaySystemTarifPrice(TarNum,PriceBuy,priceSell).transact({'from':self.userAccount,'gas':self.gas})

    def setUserDataEnergy(self,E):
        self.contract_inst.functions.setUserDataEnergy(E).transact({'from':self.userAccount,'gas':self.gas})

    def processingBillingForEnergy(self):
        self.contract_inst.functions.processBillingForEnergy().transact({'from':self.userAccount,'gas':(self.gas)*10})
