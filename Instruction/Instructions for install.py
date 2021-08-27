
# EthOmrezje -> Instructions for install 

# 1.Dowland and install Geth and Tools
    # 1.1 RPi Geth and Tools
    wget https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-arm7-1.10.8-26675454.tar.gz
    tar -xvf geth-alltools-linux-arm7-1.10.8-26675454.tar.gz
    cd geth-alltools-linux-arm7-1.10.8-26675454
    
	sudo mv geth /usr/local/bin/
	sudo mv bootnode /usr/local/bin/
	sudo mv puppeth /usr/local/bin/
    
    # 1.2 Linux Geth and Tools
    



    # 1.3 Check verison Geth and delete previous dowland files
    geth version
    rm -rf geth-alltools-linux-arm7-1.10.8-26675454.tar.gz
    rm -rf geth-alltools-linux-arm7-1.10.8-26675454


# 2.Dowland folder EthStevec Hub
   git clone https://github.com/mindolink/EthStevecDevice.git
   
   mkdir EthStevecNetwork
   cd EthStevecNetwork
   mkdir PoA5s
   mv /home/pi/EthStevecDevice/GenesisBlock/genesisPoA5s.json /home/pi/EthStevecNetwork/PoA5s/

   cd /home/pi/EthStevecNetwork/PoA5s/

   geth init --datadir /home/pi/EthStevecNetwork/PoA5s/ /home/pi/EthStevecNetwork/PoA5s/genesisPoA5s.json 
