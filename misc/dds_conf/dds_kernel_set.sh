#!/bin/bash
sudo sysctl net.ipv4.ipfrag_high_thresh=134217728
sudo sysctl net.ipv4.ipfrag_time=3
#sudo sysctl -w net.core.rmem_max=2147483647 net.core.rmem_default=67108864
#sudo sysctl -w net.core.rmem_max=2147483647 net.core.rmem_default=67108864
sudo sysctl -w net.core.wmem_max=2147483647 
sudo sysctl -w net.core.rmem_max=2147483647  

