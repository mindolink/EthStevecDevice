import numpy as np

class batteryManegmentSystem():

    def __init__(self):
        self.Pmax=20000000000
        self.Pn=[0]*5  #User Wanted Power 
        self.Pr=[0]*5   #User Allowable power
        self.Px=[0]*5   #User Local use power
        self.Pic=[0]*5  #User Requast Power From/To Grid 
        self.Poc=[0]*5  #User Assigned Power From/To Grid
        self.Py=[0]*5  #User Actual Power From/To Grid 
        self.P=[0]*5   #User Actual Power

        self.puPr=[0]*5    # Per unit Pr/Pn
        self.puPx=[0]*5    # Per unit Px/Pr
        self.puPic=[0]*5   # Per unit Pic/Pr
        self.puPoc=[0]*5   # Per unit Poc/Pr
        self.puPy=[0]*5    # Per unit Py/Pr
        self.puP=[0]*5    # Per unit (Pr+Py)/Pn

    def processAllParametersAndRestrictions(self,ReqPower,GetPower):
        self.checkUserMaxPower(ReqPower)
        self.localPower()
        self.inputPowerDataInfoForConcract()
        self.outputPowerDataInfoForConcract(GetPower)
        self.actualPowerFromOrToGrid()
        self.actualTotalPower()

    def checkUserMaxPower(self,Pn):
        self.Pn=Pn
        PsysCurPro=Pn[0]
        PsysCurCon=Pn[1]
        PsysAvaPro=Pn[2]
        PsysAvaCon=Pn[3]
        PsysReqCon=Pn[4]

        S1=PsysCurPro
        S2=PsysCurPro+PsysAvaPro
        C1=PsysCurCon
        C2=PsysCurCon+PsysReqCon
        C3=PsysCurCon+PsysReqCon+PsysAvaCon

        if(C3<self.Pmax):
            CC=1
            AC=1
            RC=1
        elif(C2<self.Pmax):
            CC=1
            AC=(self.Pmax-C2)/PsysAvaCon
            RC=1           
        elif(C1<self.Pmax):
            CC=1
            AC=0
            RC=(self.Pmax-C1)/PsysReqCon              
        else:
            CC=1
            AC=0
            RC=0

        if(S2<self.Pmax):
            CP=1
            AP=1
        elif(S1<self.Pmax):
            CP=1
            AP=(self.Pmax-S1)/PsysAvaPro
        else:
            CP=1
            AP=0

        self.puPr=[CP,CC,AP,AC,RC]
        self.Pr=np.multiply(self.puPr,Pn)
       
    def localPower(self):

        xPsCurPro=self.Pr[0]
        xPsCurCon=self.Pr[1]
        xPsAvaPro=self.Pr[2]
        xPsAvaCon=self.Pr[3]
        xPsReqCon=self.Pr[4]

        xS1=xPsCurPro
        xS2=xPsCurPro+xPsAvaPro

        xC1=xPsCurCon
        xC2=xPsCurCon+xPsReqCon
        xC3=xPsCurCon+xPsReqCon+xPsAvaCon

        if (xS1>xC3):
            xCP=xC3/xS1
            xCC=1
            xAP=0
            xAC=1
            xRC=1

        elif(xS1>xC2):
            xCP=1
            xCC=1
            xAP=0
            xAC=(xS1-xC2)/xPsAvaCon
            xRC=1

        elif(xS2>xC2):
            xCP=1
            xCC=1
            xAP=(xC2-xS1)/xPsAvaPro
            xAC=0
            xRC=1

        elif (xS2>xC1):
            xCP=1
            xCC=1
            xAP=1
            xAC=0
            xRC=(xS2-xC1)/xPsReqCon

        else:
            xCP=1
            xCC=xS2/xPsCurCon
            xAP=1
            xAC=0
            xRC=0
        
        self.puPx=[xCP,xCC,xAP,xAC,xRC]
        self.Px=(np.multiply(self.Pr,self.puPx))
      
        return (self.Px)

    def inputPowerDataInfoForConcract(self):
        self.puPic=np.subtract(1,self.puPx)
        self.Pic=np.multiply(self.Pr,self.puPic)
        return  [int(self.Pic[0]),int(self.Pic[1]),int(self.Pic[2]),int(self.Pic[3]),int(self.Pic[4])]

    def outputPowerDataInfoForConcract(self,Pgc):

        for q in range(5):
            if q>1:
                self.Poc[q]=Pgc[q-2]
                if (self.Pr[q]>0):
                    self.puPoc[q]=np.divide(self.Poc[q],self.Pr[q])
                else:
                    self.puPoc[q]=0
            else:
                self.Poc[q]=self.Pic[q]
                self.puPoc[q]=self.puPic[q]

    def actualPowerFromOrToGrid(self):
        for q in range(5):
            if q>1:
                if (self.Pic[q]<self.Poc[q]):
                    self.Py[q]=self.Pic[q]
                    self.puPy[q]=self.puPic[q]
                else:
                    self.Py[q]=self.Poc[q]
                    self.puPy[q]=self.puPoc[q]
            else:
                self.Py[q]=self.Pic[q]
                self.puPy[q]=self.puPic[q]

        return (self.Py)

    def actualTotalPower(self):
        self.puP=np.add(self.puPy,self.puPx)
        self.P=np.multiply(self.Pn,self.puP)
        return (self.P)

    def peerUnitRequestedPower(self):
        return (self.puP)


    
