#!/bin/bash
sudo sysctl net.ipv4.ipfrag_high_thresh=4194304                                  
sudo sysctl net.ipv4.ipfrag_time=30
sudo sysctl -w net.core.rmem_max=2621440 net.core.rmem_default=212992            
sudo sysctl -w net.core.wmem_max=2621440 net.core.wmem_default=212992                                                                                                    

