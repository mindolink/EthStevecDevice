import time
import carBattery,homeStorageBattery,batteryManegmentSystem,linkEthNetwork,savingMeasurements,address
import numpy as np

from datetime import datetime
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


kilo=1000
nano=1000000000

Http='http://localhost:8545'
AddressSCB=address.SCB
AddressSCC=address.SCC
PathUserInfo='./ImportData/userInfo.xlsx'
PathUserSchedule='./ImportData/userSchedule.xlsx'
PathAbiSCC='./SmartConcract/abiSystemControlingConcract.json'
PathAbiSCB='./SmartConcract/abiElectricityBillingConcract.json'

dt=30
t=1
DayName=[0,'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSTDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
##
Sec=0
Min=0
Hour=16
Day=0

StrFlg=True

TarInt=0
SystemRun=False
SystemNeedEnergy=False
EnergyMeter=0

SumArrGrdEnergy=[0]*5
SumArrGrdPower=[0]*5
SumArrTotEnergy=[0]*5
SumArrTotPower=[0]*5

#-------------Init LinkEth module-------------
ethReg=linkEthNetwork.systemControling(AddressSCC,PathAbiSCC,Http)
ethBil=linkEthNetwork.electricityBilling(AddressSCB,PathAbiSCB,Http)

#-------------Auto registration in the register of Smart Concract SCC and SCB-------------
if ethReg.getUserIndex()==0:
    ethReg.autoRegistrationNewUser()
    ethBil.autoRegistrationNewUser()
    print("Wait ............")
    time.sleep(10)


    
UserIndex=ethReg.getUserIndex()
TestNumber=ethReg.getTestNumber()
BlockNumber=ethReg.getBlock()

print(UserIndex)

#-------------Init BMS module-------------
bms=batteryManegmentSystem.batteryManegmentSystem()


#-------------Init propertise HSB module-------------
hsb=homeStorageBattery.homeStorageBattery(UserIndex,PathUserInfo)

#-------------Init propertise CAR module-------------

wbInfo = load_workbook(filename = PathUserInfo)
xlsUserCars= wbInfo['userCarProperties']
NumberOfCars=int(xlsUserCars["C"+str(UserIndex+3)].value)

if NumberOfCars>0:
    car=[0]*NumberOfCars
    for q in range (NumberOfCars):
        car[q]=carBattery.carBattery(UserIndex,q,PathUserInfo)

#-------------Read the initial values-------------

wbSchedule = load_workbook(filename = PathUserSchedule)
xlsxUserSchedule = wbSchedule["User "+str(UserIndex)]
StrDay=xlsxUserSchedule["B4"].value

StrRow=68
r=0

#-------------Loop program-------------

while r<1994:
    
    if SystemRun==True:
        
        SystemRun=ethReg.getSystemRun()
        SystemNeedEnergy=ethReg.getSystemNeedEnergy()

        if (StrFlg==True):
            print(NumberOfCars)
            sm=savingMeasurements.savingMeasurements(UserIndex,TestNumber,NumberOfCars)

            Sec=0
            Min=0
            Hour=16
            Day=0

            StrTime=time.time_ns()

            Row=StrRow
            NumSec=0
            NumAvg=0
            
            EnergyMeter=0

            SumArrGrdEnergy=[0]*5
            SumArrGrdPower=[0]*5
            SumArrGrdEnergy=[0]*5
            SumArrTotPower=[0]*5

            StrFlg=False
            PreVal=False
        
#-------------Read date and time-------------

        print(xlsxUserSchedule["B"+str(Row)].value)
        DateTime = xlsxUserSchedule["B"+str(Row)].value
        WeekNumber=datetime.date(DateTime).weekday()+1

        print("DATE: "+str(DayName[WeekNumber])+" "+str(DateTime.strftime("%d/%m/%Y")))
        print("TIME: "+str(Hour)+":"+str(Min)+":"+str(Sec))

#-------------Time tariff interval-------------

        TarNum=xlsxUserSchedule["C"+str(Row)].value
        TarInt=0

        for q in range (24):
            RowInt=Row+q
            TarLop=xlsxUserSchedule["C"+str(RowInt)].value

            if (TarLop==TarNum):
                TarInt+=1
            else:
                break

        TarIntHour=TarInt/4 #Convert to hour

#-------------Read power pasive production and consumption-------------           

        ReqPdSr=(xlsxUserSchedule["E"+str(Row)].value)
        ReqPdLd=(xlsxUserSchedule["F"+str(Row)].value)

        if ReqPdSr>ReqPdLd:
            HomNedEne=False
        else:
            HomNedEne=True


#-------------------Read the settings HSB module-------------      
        print ("")
        print("BATTERY SETINGS:")

        SOCsmart=xlsxUserSchedule["G"+str(Row)].value
        hsb.processBatterySetting(SOCsmart,WeekNumber,Hour,TarNum,TarIntHour,HomNedEne,SystemNeedEnergy)
        ReqPhsb=hsb.getRequiredPower()

#-------------------Read the settings CAR module-------------      

        ReqPcar=[0]*3

        if NumberOfCars>0:

            for q in range (NumberOfCars):

                BatOn=0
                BatSet=0
                SOCstart=0

                try:
                    Colume= get_column_letter(8+3*q)
                    BatOn=xlsxUserSchedule[str(Colume)+str(Row)].value

                    Colume= get_column_letter(9+3*q)
                    BatSet=xlsxUserSchedule[str(Colume)+str(Row)].value

                    Colume= get_column_letter(10+3*q)
                    SOCstart=xlsxUserSchedule[str(Colume)+str(Row)].value

                except:
                    BatSet=0
                    SOCstart=0

                car[q].processingBatterySetting(BatOn,BatSet,SOCstart,WeekNumber,Hour,TarNum,HomNedEne,SystemNeedEnergy)
                ReqOnePcar=car[q].getRequiredPower()
                ReqPcar=np.add(ReqPcar,ReqOnePcar)


#-------------------Network Connection-------------   

        ReqPbat=np.add(ReqPcar,ReqPhsb)

        ReqArrPower=[0]*5

        ReqArrPower[0]=ReqPdSr
        ReqArrPower[1]=ReqPdLd
        ReqArrPower[2]=ReqPbat[0]
        ReqArrPower[3]=ReqPbat[1]
        ReqArrPower[4]=ReqPbat[2]

        print ("")
        print ("REQUAST POWERS:")
        print("PdSr:"+str(round(ReqArrPower[0]/kilo,2))+"kW  PdLd:"+str(round(ReqArrPower[1]/kilo,2))+"kW  PbAvSr:"
        +str(round(ReqArrPower[2]/kilo,2))+"kW  PbAvLd:"+str(round(ReqArrPower[3]/kilo,2))+"kW  PbRqLd:"
        +str(round(ReqArrPower[4]/kilo,2))+"kW")


#-------------------Control BMS system limitations-------------    
        GetArrPower=ethReg.getUserDataPower()
        bms.processAllParametersAndRestrictions(ReqArrPower,GetArrPower)
        SndReqPower=bms.inputPowerDataInfoForConcract()


#-------------------Sending data power requirements and wishes in ETH-------------    

        NetCon=(xlsxUserSchedule["D"+str(Row)].value)

        if NetCon=="OFF":
            SndReqPower[2]=0
            SndReqPower[3]=0
            SndReqPower[4]=0

        if ethReg.checkBlock():
            ethReg.setUserDataPower(SndReqPower)

    
        
#-------------------Set system power-------------    

        SystemNeedEnergy=ethReg.getSystemNeedEnergy()
        GetArrPower=ethReg.getUserDataPower()
        bms.processAllParametersAndRestrictions(ReqArrPower, GetArrPower)

        ActArrTotPower=bms.actualTotalPower()
        ActArrGrdPower=bms.actualPowerFromOrToGrid()

        SumArrTotPower=np.add(SumArrTotPower,ActArrTotPower)
        SumArrGrdPower=np.add(SumArrGrdPower,ActArrGrdPower)

        puActArrPower=bms.peerUnitRequestedPower()


        print ("")
        print ("ACTUAL POWERS IN SEGMENT:")
        print("PdSr:"+str(round(ActArrTotPower[0]/kilo,2))+"kW  PdLd:"+str(round(ActArrTotPower[1]/kilo,2))+"kW  PbAvSr:"
        +str(round(ActArrTotPower[2]/kilo,2))+"kW  PbAvLd:"+str(round(ActArrTotPower[3]/kilo,2))+"kW  PbRqLd:"
        +str(round(ActArrTotPower[4]/kilo,2))+"kW")
        print ("")


#-------------------Set device power-------------   

        hsb.setBatteryPower(puActArrPower)

        if NumberOfCars>0:
            for q in range (NumberOfCars):
                car[q].setBatteryPower(puActArrPower)


#-------------------Internal time-------------------
        
        NumAvg+=1
        NumSec+=1
        Sec+=dt

        if Sec>=60:
            Min+=1
            Sec=0

        if Min>=60:
            Hour+=1
            Min=0

        if Hour>=24:
            Day+=1
            Hour=0


#----------------------Update meausrments------------------------

        SumArrTotEnergy+=np.multiply(ActArrTotPower,dt)
        SumArrGrdEnergy+=np.multiply(ActArrGrdPower,dt)
        
        hsb.updateBatteryValues(dt)

        for q in range (NumberOfCars):
            car[q].updateBatteryValues(dt)


#-------------------Sending data energy production and consumption in ETH-------------  

        if ((Min==0 or Min==15 or Min==30 or Min==45) and Sec==dt):

            if Min==0:
                DateTimeStr=(DateTime.strftime("%d/%m/%Y %H"))+":0"+str(Min)
            else:
                DateTimeStr=(DateTime.strftime("%d/%m/%Y %H"))+":"+str(Min)

#-------------------Sending data energy production and consumption in ETH-------------  

        if ((Min==0 or Min==15 or Min==30 or Min==45) and Sec==0):

            xlsxSystemTarifPrices = wbInfo["systemTariffPrices"]
            TarNumPre=xlsxUserSchedule["C"+str(Row)].value

            PriceBuy=xlsxSystemTarifPrices["C"+str(TarNumPre+2)].value
            PriceSell=xlsxSystemTarifPrices["D"+str(TarNumPre+2)].value
            
            ethBil.modifaySystemTarifPrice(int(TarNumPre),int(PriceBuy), int(PriceSell))
            ethBil.setUserDataEnergy([int(SumArrGrdEnergy[0]),int(SumArrGrdEnergy[1]),int(SumArrGrdEnergy[2]),int(SumArrGrdEnergy[3]),int(SumArrGrdEnergy[4])])
            
       
#-------------------Storing power and energy measurement data------------- 

            AvgArrTotPower=np.divide(SumArrTotPower,NumAvg)

            AvgPin=0
            AvgPout=0
            SumEin=0
            SumEout=0

            for q in range(5):
                if q==0 or q==2:
                    AvgPout+=SumArrGrdPower[q]/NumAvg
                    SumEout+=SumArrGrdEnergy[q]

                else:
                    AvgPin+=SumArrGrdPower[q]/NumAvg
                    SumEin+=SumArrGrdEnergy[q]

            sm.safeBasicMeasurements(DateTimeStr, AvgPin,AvgPout, AvgArrTotPower,SumEin, SumEout, SumArrTotEnergy)

            EnergyMeter=SumEin-SumEout

            if (hsb.BatOn==True):
                InfoBat=hsb.getBatteryInfo(NumAvg)
                sm.safeHomeBatteryMeasurements(InfoBat)

            if (NumberOfCars>0):
                for q in range (NumberOfCars):
                    InfoBat=car[q].getBatteryInfo(NumAvg)
                    sm.safeCarBatteryMeasurements(q, InfoBat)

            SumArrGrdEnergy=[0]*5
            SumArrTotEnergy=[0]*5

            SumArrGrdPower=[0]*5
            SumArrTotPower=[0]*5

            NumAvg=0


            MonayWalletCent=ethBil.getUserWalletInCent()
            PriceForEnergyCent=ethBil.getUserFinalEnergyPriceInCent()

            if PreVal==True:
                sm.safeCashBalance(MonayWalletCent, PriceForEnergyCent)
            
            PreVal=True


            Row+=1



#-------------------Billing for energy production and consumption in ETH-------------------

        if ((Min==5 or Min==20 or Min==35 or Min==50) and Sec==0):

            ethBil.processingBillingForEnergy()



#-------------------External time-------------------

        while (StrTime+(NumSec*t)*nano>time.time_ns()):
            None


#-------------------Waight fort strat program-------------------
    else:
        StrFlg=True
        SystemRun=ethReg.getSystemRun()
        print("System don't work")