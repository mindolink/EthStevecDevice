// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
//import "remix_tests.sol"; // this import is automatically injected by Remix.
//import "../contracts/3_Ballot.sol";


contract systemRegulationSmartConcract 
{   
    uint public numberOfUser;
    uint blockNumber=0;
    uint N=10000;   //Per-Unit Multiplay
    uint blockTest=1;
    //Information abaout owner of system/grid
    address OwnAddress;
    
    //Informtion about system/grid
    uint public sysMaxPower=15000;   //[W]
    uint public sysTarNum;
    bool public sysRunSta;
    uint public TestNumber;

    //Users information
    mapping (uint=>address) usrAddress;
    mapping (address=>uint) usrIndex;
    mapping (address=>bool) usrRegistration;
    mapping (address=>uint) usrActive;
    mapping (address=>uint)  usrPdSr;
    mapping (address=>uint)  usrPdLd;
    mapping (address=>uint)  usrPbAvSr;
    mapping (address=>uint)  usrPbAvLd;
    mapping (address=>uint)  usrPbRqLd;
    

    bool [] usrAlredySendData;

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
    
    
    function autoRegistrationNewUser() public checkNonRegistrationOfUser
    {   
        numberOfUser+=1;
        usrRegistration[msg.sender]= true;
        usrIndex[msg.sender]=numberOfUser;
        usrAddress[usrIndex[msg.sender]]=msg.sender;
    }
    

    
    function setUserDataPower(uint [] memory P) public checkRegistrationOfUser
    { 
        usrPdSr[msg.sender]=P[0];
        usrPdLd[msg.sender]=P[1];
        usrPbAvSr[msg.sender]=P[2];
        usrPbAvLd[msg.sender]=P[3];
        usrPbRqLd[msg.sender]=P[4];
        usrActive[msg.sender]=block.number;
        blockNumber=block.number;
    }

    function sumSystemPower() public view returns(uint[5] memory)
    {
        uint sysPdSr=0;
        uint sysPdLd=0;
        uint sysPbAvSr=0;
        uint sysPbAvLd=0;
        uint sysPbRqLd=0;
        
        for(uint i=1;i<=numberOfUser;i++)
        {
            if (usrActive[usrAddress[i]]==(blockNumber))
            {
                sysPdSr+=usrPdSr[usrAddress[i]];
                sysPdLd+=usrPdLd[usrAddress[i]];
                sysPbAvSr+=usrPbAvSr[usrAddress[i]];
                sysPbAvLd+=usrPbAvLd[usrAddress[i]];
                sysPbRqLd+=usrPbRqLd[usrAddress[i]];
            }
        }

        return([sysPdSr,sysPdLd,sysPbAvSr,sysPbAvLd,sysPbRqLd]);
    }

    function checkMaxPowerOfSystem() public view returns(uint [3] memory)
    {
        uint [5] memory sysPsum=sumSystemPower();
        
        uint sysPdSr=sysPsum[0];
        uint sysPdLd=sysPsum[1];
        uint sysPbAvSr=sysPsum[2];
        uint sysPbAvLd=sysPsum[3];
        uint sysPbRqLd=sysPsum[4];
    
        uint puPbAvSr=0;
        uint puPbAvLd=0;
        uint puPbRqLd=0;
        
        if (sysMaxPower>(sysPdLd+sysPbAvLd+sysPbRqLd))
        {
            puPbAvLd=N;
            puPbRqLd=N;
        }
        else if (sysMaxPower>(sysPdLd+sysPbRqLd))
        {
            puPbAvLd=(N*(sysMaxPower-(sysPdLd+sysPbRqLd)))/sysPbAvLd;
            puPbRqLd=N;
        }
        else if (sysMaxPower>sysPdLd)
        {
            puPbAvLd=0;
            puPbRqLd=(N*(sysMaxPower-(sysPdLd)))/sysPbRqLd;
        }
        else
        {
            puPbAvLd=0;
            puPbRqLd=0;
        }       
        
        if (sysMaxPower>(sysPdSr+sysPbAvSr))
        {
            puPbAvSr=N;
        }  
        
        else if (sysMaxPower>sysPdSr)
        {
            puPbAvSr=(N*(sysMaxPower-sysPdSr))/sysPbAvSr;
        }
        else
        {
            puPbAvSr=0;
        }
        
        return ([puPbAvSr,puPbAvLd,puPbRqLd]);
        
    }


    function getUserDataPower() public view returns(uint [3] memory)
    {
        uint [3] memory puPmax= checkMaxPowerOfSystem();
        uint [5] memory sysPsum=sumSystemPower();
    
    
        uint sysMaxPbAvSr=(sysPsum[2]*puPmax[0])/N;
        uint sysMaxPbAvLd=(sysPsum[3]*puPmax[1])/N;
        uint sysMaxPbRqLd=(sysPsum[4]*puPmax[2])/N;
    
        uint S1=sysPsum[0];      
        uint S2=sysPsum[0]+sysMaxPbAvSr;
    
        uint C2=sysPsum[1]+sysMaxPbRqLd;
        uint C3=sysPsum[1]+sysMaxPbAvLd+sysMaxPbRqLd;

        
        uint puX;
        uint getPbAvSr;
        uint getPbAvLd;
        uint getPbRqLd;
        
        if (usrActive[msg.sender]==(blockNumber))
        {
            if (S1>C3)
            {
                getPbAvSr=0;
                getPbAvLd=(usrPbAvLd[msg.sender]*puPmax[1])/N;
                getPbRqLd=(usrPbRqLd[msg.sender]*puPmax[2])/N;
            }
            
            else if (S1>C2)
            {   
                puX=(N*(S1-C2))/sysMaxPbAvLd;
                getPbAvSr=0;
                getPbAvLd=(usrPbAvLd[msg.sender]*puPmax[1]*puX)/(N*N);
                getPbRqLd=(usrPbRqLd[msg.sender]*puPmax[2])/N;
            }
            
            else if (S2>C2)
            {   
                puX=(N*(C2-S1))/sysMaxPbAvSr;
                getPbAvSr=(usrPbAvSr[msg.sender]*puPmax[0]*puX)/(N*N);
                getPbAvLd=0;
                getPbRqLd=(usrPbRqLd[msg.sender]*puPmax[2])/N;
            }
            else
            {
                getPbAvSr=(usrPbAvSr[msg.sender]*puPmax[0])/N;
                getPbAvLd=0;
                getPbRqLd=(usrPbRqLd[msg.sender]*puPmax[2])/N;
            }
        }   
        else
        {
            getPbAvSr=0;
            getPbAvLd=0;
            getPbRqLd=0;
        }
        
        return ([getPbAvSr,getPbAvLd,getPbRqLd]);
    }

    function getIfSystemNeedEnergy()public view returns(bool)
    {
        uint [5] memory sysPsum=sumSystemPower();
        bool sysNedEne;
        
        if (sysPsum[0]<=(sysPsum[1]+sysPsum[4]))
        {
            sysNedEne=true;
        }
        else
        {
            sysNedEne=false;
        }
        
        return (sysNedEne);
    }


    function modifaySystemTarifeNumber(uint _sysTarNum) public checkRegistrationOfUser
    {
        sysTarNum=_sysTarNum;
    }

    function modifaySystemRunningStatus() public
    {
        
        if (sysRunSta==true)
        {
            sysRunSta=false;
        }
        else 
        {
            sysRunSta=true;
        } 
    }

    function modifaySystemMaxPower(uint _sysMaxPower) public
    {
        sysMaxPower=_sysMaxPower;
    }

    function modifayTestNUmber(uint _TestNumber) public
    {
        TestNumber=_TestNumber;
    }

    function getUserIndex() public view returns(uint) 
    {
        return(usrIndex[msg.sender]);
    }
    
    function getTestNumber() public view returns(uint) 
    {
        return(TestNumber);
    }
    
    function registrationNewUser(address _Address) public checkRegistrationOfUser
    {   
        numberOfUser++;
        usrRegistration[_Address]= true;
        usrIndex[_Address]=numberOfUser++;
        usrAddress[usrIndex[_Address]]=_Address;
    }
    
}