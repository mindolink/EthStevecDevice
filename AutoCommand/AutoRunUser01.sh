




geth --datadir "./home/pi/EthOmrezje/Network/PoA5s" --miner.etherbase 1 --unlock 1 --port 50501 --ethstats node1:test@89.142.195.19:3000 --mine --syncmode "full" --networkid 1994 --http --http.addr "localhost" --http.corsdomain "https://remix.ethereum.org" --http.port 8545 --nat "any" --http.api "web3,eth,net,personal,miner,debug,txpool,admin" --bootnodes "enode://19c8fd97b5edc99f97170462400a38c2e7c9347c1a96e15b7f623562b9d0a637e2a70b749077c38d1a07b34f802985521403eb6b69bf30806993a1623c53be10@192.168.1.107:31313" --keystore /home/pi/EthOmrezje/UserHash/ --password /home/pi/EthOmrezje/UserHash/password.sec --allow-insecure-unlock