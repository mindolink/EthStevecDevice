// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

//import "remix_tests.sol"; // this import is automatically injected by Remix.
//import "../contracts/3_Ballot.sol";

contract electricityBillingConcract {
    
    
    int N=100000;
    
    mapping(uint => address) usrAddress;
    mapping(address => uint) usrIndex;
    mapping(address => bool) usrRegistration;
    mapping(address => int)  usrWalletNanoCent;
    mapping(address => int)  usrEnergyPriceNanoCent;
    
    mapping(address => bool) usrActive;
    mapping(address => int)  usrEdSr;
    mapping(address => int)  usrEdLd;
    mapping(address => int)  usrEbAvSr;
    mapping(address => int)  usrEbAvLd;
    mapping(address => int)  usrEbRqLd;

    address ownAddress;
    int  ownWalletNanoCent=0;
    int  ownEnergyDistributed=0;
    int  ownEnergyPriceNanoCent=0;
    
    int Q=0;
    bool flgProsecing=true;
    uint blockNumber;
    
    uint public numberOfUser;
    
    int public TarNum = 3;
    int public B3Wh = 8;
    int public S3Wh = 24;
    int public B2Wh = 8;
    int public S2Wh = 24;
    int public B1Wh = 16;
    int public S1Wh = 16;

    int nano=1000000000;
    
    int nB3Ws=(nano*B3Wh)/3600000; //Buy price Tariff 3 in nanoCent for Ws
    int nS3Ws=(nano*S3Wh)/3600000; //Sell price price Tariff 3 in nanoCent for Ws
    int nB2Ws=(nano*B2Wh)/3600000; //Buy price Tariff 2 in nanoCent for Ws
    int nS2Ws=(nano*S2Wh)/3600000; //Sell price Tariff 2 in nanoCent for Ws
    int nB1Ws=(nano*B1Wh)/3600000; //Buy price Tariff 1 in nanoCent for Ws
    int nS1Ws=(nano*S1Wh)/3600000; //Sell price Tariff 1 in nanoCent for Ws

    modifier checkNonRegistrationOfUser
    {
        require(usrRegistration[msg.sender]==false);
        _;
    }
    
    
    modifier checkRegistrationOfUser
    {
        require(usrRegistration[msg.sender]==true);
        _;
    }
    
        modifier checkIfProcessBillingAlradyMade
    {
        require(flgProsecing==false);
        _;
    }


    function autoRegistrationNewUser() public checkNonRegistrationOfUser
    {   
        numberOfUser+=1;
        usrRegistration[msg.sender]= true;
        usrIndex[msg.sender]=numberOfUser;
        usrAddress[usrIndex[msg.sender]]=msg.sender;
    }
    
    
    function setUserDataEnergy(int[] memory E) public
    { 
        usrEdSr[msg.sender]=E[0];   //User unRegulated production power
        usrEdLd[msg.sender]=E[1];   //User unRegulated consuption power
        usrEbAvSr[msg.sender]=E[2];   //Avalible production power
        usrEbAvLd[msg.sender]=E[3];   //Avalible consuption power
        usrEbRqLd[msg.sender]=E[4];   //Reguasted consuption power 
        
        usrActive[msg.sender]=true;
        flgProsecing=false;
    }


    function sumSystemEnergy() public view returns(int[5] memory)
    {
        int sysEdSr=0;
        int sysEdLd=0;
        int sysEbAvSr=0;
        int sysEbAvLd=0;
        int sysEbRqLd=0;
        
        for(uint i=1;i<=numberOfUser;i++)
        {
            if (usrActive[usrAddress[i]]==true)
            {
                sysEdSr+=usrEdSr[usrAddress[i]];
                sysEdLd+=usrEdLd[usrAddress[i]];
                sysEbAvSr+=usrEbAvSr[usrAddress[i]];
                sysEbAvLd+=usrEbAvLd[usrAddress[i]];
                sysEbRqLd+=usrEbRqLd[usrAddress[i]];
            }
        }

        return([sysEdSr,sysEdLd,sysEbAvSr,sysEbAvLd,sysEbRqLd]);
    }


    function processBillingForEnergy() public checkIfProcessBillingAlradyMade
    {
        int [5] memory Esum=sumSystemEnergy();
        
        int sysCon=Esum[1]+Esum[3]+Esum[4];
        int sysPro=Esum[0]+Esum[2];
        
        int sysProBaseCost;
        int sysConBaseCost;
        int sysProFinalCost;
        int sysConFinalCost;
        int sysDif;
        
        int puPro;
        int puCon;
        
        sysProBaseCost=(Esum[0]*nS1Ws)+(Esum[2]*nS2Ws);   
        sysConBaseCost=(Esum[1]+Esum[4])*nB1Ws+(Esum[3]*nB2Ws);
        
        
        if  (sysCon<sysPro)
        {   
            sysDif=sysPro-sysCon;
            sysProFinalCost=sysConBaseCost+nB3Ws*sysDif;
            sysConFinalCost=sysConBaseCost;
            
            if (sysProBaseCost>0)
            {            
                puPro=(N*sysProFinalCost)/sysProBaseCost;
            }
            else
            {
                puPro=0;
            }
            
            puCon=N;
            
            ownEnergyPriceNanoCent=nB3Ws*sysDif;
            ownWalletNanoCent-=nB3Ws*sysDif;
            ownEnergyDistributed=sysDif;
        }
        else
        {   
            sysDif=sysCon-sysPro;
            sysProFinalCost=sysProBaseCost;
            sysConFinalCost=sysProBaseCost+nS3Ws*sysDif;
            
            puPro=N;
            
            if (sysConBaseCost>0)
            {
                puCon=(N*sysConFinalCost)/sysConBaseCost;
            }
            else
            {
                puCon=0;
            }
            
            ownEnergyPriceNanoCent=-nS3Ws*sysDif;
            ownWalletNanoCent+=nS3Ws*sysDif;
            ownEnergyDistributed=sysDif;
        }
        
        
        for(uint i=1;i<=numberOfUser;i++)
        {   
            if (usrActive[usrAddress[i]]==true)
            {
                int usrProPriceNanoCent=((puPro*nS1Ws*usrEdSr[usrAddress[i]])/N)+((puPro*nS2Ws*usrEbAvSr[usrAddress[i]])/N);
                int usrConPriceNanoCent=((puCon*nB1Ws*usrEdLd[usrAddress[i]])/N)+((puCon*nB2Ws*usrEbAvLd[usrAddress[i]])/N)+((puCon*nB1Ws*usrEbRqLd[usrAddress[i]])/N);
                
                usrEnergyPriceNanoCent[usrAddress[i]]=usrConPriceNanoCent-usrProPriceNanoCent;
                usrWalletNanoCent[usrAddress[i]]+=usrEnergyPriceNanoCent[usrAddress[i]];
                usrActive[usrAddress[i]]=false;
            }
            else
            {
                usrEdSr[usrAddress[i]]=0;
                usrEdLd[usrAddress[i]]=0;
                usrEbAvSr[usrAddress[i]]=0;
                usrEbAvLd[usrAddress[i]]=0;
                usrEbRqLd[usrAddress[i]]=0; 
                
            }
        }
        
        flgProsecing=true;
        
    }
    
    function getUserFinalEnergyPriceInCent() public view returns(int)
    {
        return(usrEnergyPriceNanoCent[msg.sender]/nano);
    }
    
    function getUserWalletInCent() public view returns(int)
    {
        return(usrWalletNanoCent[msg.sender]/nano);
    }
    
        function getUserIndex() public view returns(uint) 
    {
        return(usrIndex[msg.sender]);
    }
    
    
    function modifaySystemTarifPrice(int _TarNum,int _B3Wh, int _S3Wh) public
    {   
        TarNum=_TarNum;
        S3Wh = _S3Wh;
        B3Wh = _B3Wh;

        B2Wh = (B3Wh*(100+Q))/100;
        S2Wh = (S3Wh*(100-Q))/100;
        
        B1Wh = B3Wh+((S3Wh-B3Wh)/2);
        S1Wh = B1Wh;

        nB3Ws=(nano*B3Wh)/3600000; //Buy price Tariff 3 in nanoCent for Ws
        nS3Ws=(nano*S3Wh)/3600000; //Sell price price Tariff 3 in nanoCent for Ws
        nB2Ws=(nano*B2Wh)/3600000; //Buy price Tariff 2 in nanoCent for Ws
        nS2Ws=(nano*S2Wh)/3600000; //Sell price Tariff 2 in nanoCent for Ws
        nB1Ws=(nano*B1Wh)/3600000; //Buy price Tariff 1 in nanoCent for Ws
        nS1Ws=(nano*S1Wh)/3600000; //Sell price Tariff 1 in nanoCent for Ws   
    }
    

    
}