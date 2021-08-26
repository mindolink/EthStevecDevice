import time
import carBattery,homeStorageBattery,batteryManegmentSystem,linkEthNetwork,savingMeasurements,address
import numpy as np

from datetime import datetime
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


k=1000
nano=1000000000
a=0
UserGethUnlockAccount=0
Http='http://localhost:8545'
AddrEB=address.addressConcractElectricityBilling
AddrSC=address.addressConcractSystemRegulation
PathUserInfo='./ImportData/userInfo.xlsx'
PathUserSchedule='./ImportData/userSchedule.xlsx'
PathAbiSC='./SmartConcract/abiSystemControlingConcract.json'
PathAbiEB='./SmartConcract/abiElectricityBillingConcract.json'
dt=10
t=1
DayName=[0,'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSTDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

Sec=0
Min=0
Hour=0
Day=0

SecFlg=0
AvgFlg=1
StrFlg=False
TarInt=0
SysRun=False
SysNedEne=False
EnergyMeter=0

ReqArrPower=[0]*5
SndArrPower=[0]*5
GetArrPower=[0]*5
ActArrPower=[0]*5
SumArrGrdEnergy=[0]*5
SumArrGrdPower=[0]*5
SumArrTotEnergy=[0]*5
SumArrTotPower=[0]*5


#Init moduls parameters
ethReg=linkEthNetwork.systemControling(AddrSC,PathAbiSC,Http,UserGethUnlockAccount)
ethBil=linkEthNetwork.electricityBilling(AddrEB,PathAbiEB,Http,UserGethUnlockAccount)

BlockNumber=ethReg.getBlock()


#Registration in SmartConcract

if ethReg.getUserIndex()==0:
    ethReg.autoRegistrationNewUser()
    time.sleep(5)

if ethBil.getUserIndex()==0:
    ethBil.autoRegistrationNewUser()
    time.sleep(5)


UserNumber=ethReg.getUserIndex()
TestNumber=ethReg.getTestNumber()
#Init all parameters BMS
bms=batteryManegmentSystem.batteryManegmentSystem()

#Init all parameters Home storage Batery
Hsb=homeStorageBattery.homeStorageBattery(UserNumber,PathUserInfo)


#----------------------INIT PROPERTISE USER CARS------------------------------------------
wbInfo = load_workbook(filename = PathUserInfo)
xlsUserCars= wbInfo['userCarProperties']
NumberOfCars=int(xlsUserCars["C"+str(UserNumber+3)].value)


if NumberOfCars>0:
    Car=[0]*NumberOfCars
    for q in range (NumberOfCars):
        Car[q]=carBattery.carBattery(UserNumber,q,PathUserInfo)


#Init parameters for saving values

sm=savingMeasurements.savingMeasurements(UserNumber,TestNumber,NumberOfCars)

#---------------------------READ PARAMETERS FROM ETH NETWORK-----------------------------

SysRun=ethReg.getSystemRuning()
SysNedEne=ethReg.getIfSystemNeedEnergy()

r=0

wbSchedule = load_workbook(filename = PathUserSchedule)
xlsxUserSchedule = wbSchedule["User "+str(UserNumber)]

StrDay=xlsxUserSchedule["B4"].value
StrHour=xlsxUserSchedule["C4"].value


#----------------------OPEN FOLDER SCHEDULE USER---------------------------------
while r<23:
    
    if SysRun==True:

        if (StrFlg==False):

            StrTime=time.time_ns()
            StrSec=0
            AvgFlg=1
            StrFlg=True

        row=(Day*24)+Hour+4
        
        DateTime = xlsxUserSchedule["B"+str(row)].value
        WeekNumber=datetime.date(DateTime).weekday()+1
        print("DATE: "+str(DayName[WeekNumber])+" "+str(DateTime.strftime("%d/%m/%Y")))
        print("TIME: "+str(Hour)+":"+str(Min)+":"+str(Sec))

        SysNedEne=ethReg.getIfSystemNeedEnergy()

        if Min==0:
            DateTimeStr=(DateTime.strftime("%d/%m/%Y %H"))+":0"+str(Min)
        else:
            DateTimeStr=(DateTime.strftime("%d/%m/%Y %H"))+":"+str(Min)


    #-------------------LOOKING DURATION PRICE ENERGY TARIFF-------------------------
        TarNum=xlsxUserSchedule["C"+str(row)].value
        TarInt=0

        for q in range (24):
            rowLop=row+q
            TarLop=xlsxUserSchedule["C"+str(rowLop)].value

            if (TarLop==TarNum):
                TarInt+=1
            else:
                break
    #-----------------------POWER PROM DEVICE AND PV--------------------------------

        ReqPdSr=(xlsxUserSchedule["D"+str(row)].value)*1000
        ReqPdLd=(xlsxUserSchedule["E"+str(row)].value)*1000

        if ReqPdSr>ReqPdLd:
            HomNedEne=False
        else:
            HomNedEne=True


    #-------------------LOOKING HOME AND CARS SETTINGS ------------------------------
        print ("")
        print("BATTERY SETINGS:")
        
        SOCsmart=xlsxUserSchedule["F"+str(row)].value
        Hsb.processBatterySetting(SOCsmart,WeekNumber,Hour,TarNum,TarInt,HomNedEne,SysNedEne)
        ReqPhsb=Hsb.getRequiredPower()

        ReqPcar=[0]*3

        if NumberOfCars>0:

            for q in range (NumberOfCars):

                BatOn=0
                BatSet=0
                SOCstart=0

                try:
                    colume= get_column_letter(7+3*q)
                    BatOn=xlsxUserSchedule[str(colume)+str(row)].value

                    colume= get_column_letter(8+3*q)
                    BatSet=xlsxUserSchedule[str(colume)+str(row)].value

                    colume= get_column_letter(9+3*q)
                    SOCstart=xlsxUserSchedule[str(colume)+str(row)].value

                except:
                    BatSet=0
                    SOCstart=0

                Car[q].processingBatterySetting(BatOn,BatSet,SOCstart,WeekNumber,Hour,TarNum,HomNedEne,SysNedEne)
                ReqOnePcar=Car[q].getRequiredPower()
                ReqPcar=np.add(ReqPcar,ReqOnePcar)

    #---------------------TOTAL CONSUPTION ----------------------
        
        ReqPbat=np.add(ReqPcar,ReqPhsb)

        ReqArrPower[0]=ReqPdSr
        ReqArrPower[1]=ReqPdLd
        ReqArrPower[2]=ReqPbat[0]
        ReqArrPower[3]=ReqPbat[1]
        ReqArrPower[4]=ReqPbat[2]

        print ("")
        print ("REQUAST POWERS:")
        print("PdSr:"+str(round(ReqArrPower[0]/k,2))+"kW  PdLd:"+str(round(ReqArrPower[1]/k,2))+"kW  PbAvSr:"
        +str(round(ReqArrPower[2]/k,2))+"kW  PbAvLd:"+str(round(ReqArrPower[3]/k,2))+"kW  PbRqLd:"
        +str(round(ReqArrPower[4]/k,2))+"kW")


    #----------CHECK LIMITATIONS HAUSE MAX POWER WITH BMS---------------

        bms.processAllParametersAndRestrictions(ReqArrPower,GetArrPower)
        SndReqPower=bms.inputPowerDataInfoForConcract()

    #------------SEND AND GET INFO POWER FROM ETH NETWORK----------------

        if ethReg.checkBlock():
            #Send demanded and requasted data:
            ethReg.setUserDataPower(SndReqPower)
            #ethReg.modifaySystemTarifeNumber(TarNum)

            SysNedEne=ethReg.getIfSystemNeedEnergy()
            GetArrPower=ethReg.getUserDataPower()
            #Get assagned data
        
        
        bms.processAllParametersAndRestrictions(ReqArrPower, GetArrPower)

            
    #------------------GET ACTUAL POWERS-----------------------------------
        
        ActArrTotPower=bms.actualTotalPower()
        ActArrGrdPower=bms.actualPowerFromOrToGrid()

        SumArrTotPower=np.add(SumArrTotPower,ActArrTotPower)
        SumArrGrdPower=np.add(SumArrGrdPower,ActArrGrdPower)

        puActArrPower=bms.peerUnitRequestedPower()


        print ("")
        print ("ACTUAL POWERS IN SEGMENT:")
        print("PdSr:"+str(round(ActArrTotPower[0]/k,2))+"kW  PdLd:"+str(round(ActArrTotPower[1]/k,2))+"kW  PbAvSr:"
        +str(round(ActArrTotPower[2]/k,2))+"kW  PbAvLd:"+str(round(ActArrTotPower[3]/k,2))+"kW  PbRqLd:"
        +str(round(ActArrTotPower[4]/k,2))+"kW")
        print ("")


    #---------------- SET POWER INFO ON BATERY -----------------

        Hsb.setBatteryPower(puActArrPower)

        if NumberOfCars>0:
            for q in range (NumberOfCars):
                Car[q].setBatteryPower(puActArrPower)


    #-------- SEND  ENERGY INFO IN ETEHREUM NETWORK ---------

        if ((Min==0 or Min==15 or Min==30 or Min==45) and Sec==0):

            try:
                TarNumPre=(xlsxUserSchedule["C"+str(row)].value)*1

            except:
                TarNumPre=xlsxUserSchedule["C"+str(row-1)].value

            xlsxSystemTarifPrices = wbInfo["systemTariffPrices"]
            PriceBuy=xlsxSystemTarifPrices["C"+str(TarNumPre+2)].value
            PriceSell=xlsxSystemTarifPrices["D"+str(TarNumPre+2)].value
        

            ethBil.modifaySystemTarifPrice(int(TarNumPre),int(PriceBuy), int(PriceSell))
            ethBil.setUserDataEnergy([int(SumArrGrdEnergy[0]),int(SumArrGrdEnergy[1]),int(SumArrGrdEnergy[2]),int(SumArrGrdEnergy[3]),int(SumArrGrdEnergy[4])])
            
       

    #------------------Safe measurment of energy and avg power-------------------------

            AvgArrTotPower=np.divide(SumArrTotPower,AvgFlg)
            
            AvgPin=0
            AvgPout=0
            SumEin=0
            SumEout=0

            for q in range(5):
                if q==0 or q==2:
                    AvgPout+=SumArrGrdPower[q]/AvgFlg
                    SumEout+=SumArrGrdEnergy[q]

                else:
                    AvgPin+=SumArrGrdPower[q]/AvgFlg
                    SumEin+=SumArrGrdEnergy[q]

            sm.safeBasicMeasurements(DateTimeStr, AvgPout, AvgPin, AvgArrTotPower, SumEin, SumEout, SumArrTotEnergy)


            if (Hsb.BatOn==True):
                InfoBat=Hsb.getBatteryInfo(AvgFlg)
                sm.safeHomeBatteryMeasurements(InfoBat)

            if (NumberOfCars>0):
                for q in range (NumberOfCars):
                    InfoBat=Car[q].getBatteryInfo(AvgFlg)
                    sm.safeCarBatteryMeasurements(q, InfoBat)


            SumArrGrdEnergy=[0]*5
            SumArrTotEnergy=[0]*5
            SumArrGrdPower=[0]*5
            SumArrTotPower=[0]*5

            AvgFlg=0
            
    #---------------------ETH BILING PREVIOUS SENDED PRICE-------------------------

        if ((Min==5 or Min==20 or Min==35 or Min==50) and Sec==dt):

            ethBil.processingBillingForEnergy()

    #----------------------SAVE PRICE AND WALLET WALLEUS----------------------------------

        if ((Min==10 or Min==25 or Min==40 or Min==55) and Sec==dt):

            MonayWalletCent=ethBil.getUserWalletInCent()
            PriceForEnergyCent=ethBil.getUserFinalEnergyPriceInCent()

            sm.safeCashBalance(MonayWalletCent, PriceForEnergyCent)


    #--------------- TIME SLEEP----------------------------------
        
        AvgFlg+=1
        StrSec+=1
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
            
    #----------------------UPDATE VALUES ------------------------

        SumArrTotEnergy+=np.multiply(ActArrTotPower,dt)
        SumArrGrdEnergy+=np.multiply(ActArrGrdPower,dt)
        
        Hsb.updateBatteryValues(dt)

        for q in range (NumberOfCars):
            Car[q].updateBatteryValues(dt)

        SysRun=ethReg.getSystemRuning()


        print("---------------------------------------------------------")

        a=1
        while (StrTime+(StrSec*t)*nano>time.time_ns()):
            None

        
    else:

        Sec=0
        Min=0
        Hour=0
        Day=0

        AvgFlg=0
        StrFlg=False

        SysRun=False
        SysNedEne=False

        EnergyMeter=0
        
        ReqArrPower=[0]*5
        SndArrPower=[0]*5
        GetArrPower=[0]*5
        ActArrPower=[0]*5

        ActArrGrdEnergy=[0]*5
        SumArrGrdPower=[0]*5
        ActArrTotEnergy=[0]*5
        SumArrTotPower=[0]*5

        if a==1:
            savingMeasurements.savingMeasurements(UserNumber,TimeOfTest,NumberOfCars)
            a=0

        print("System don't work")

        SysRun=ethReg.getSystemRuning()