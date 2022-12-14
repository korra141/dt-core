# Communication node using dts devel  

This is intended for the **Stop Sign standalone demo**.  
Just place the bots (2 or more) at a Stop intersection and run the code for all the bots. The code will run indefinitely.  

To run the code make sure you have an up to date dts shell and duckiebot.
You can run the following commands:  
`dts update`  
`dts desktop update`  
`dts duckiebot update YOURBOTNAME`  

IMPORTANT: For a accurate LED flashing consistently, always execute the following command after the bot has been reboot:  
`ssh duckie@YOURBOTNAME.local "echo '400000' | sudo tee /sys/bus/i2c/devices/i2c-1/bus_clk_rate"`  

First you need to build it on the bot  
`dts devel build -f -H YOURBOTNAME.local`  

Run the code from this repo root (dt-core)  
`dts devel run -H YOURBOTNAME.local`  

The bot will start flashing its LEDs and the negotiation will run indefinitely. Bots that get the priority will set their LEDs to GREEN. Bots that don't get priority in the current negotiation cycle will set their LEDs to BLUE. There is a possibility a bot reaches a time-out state if it does not get a priority for a certain number of cycles (defined in `BaseComNode` as `TIME_OUT_SEC`).  

NOTE: For the demo, if a bot reaches GREEN light we can simply stop it.  

INFO: The code is configured that the `default.sh` script (`launchers/default.sh`) invokes the command `dt-exec roslaunch --wait duckietown_demos communication.launch`. You can change this if needed.  


# dt-core

Status:
[![Build Status](https://ci.duckietown.org/buildStatus/icon?job=Docker+Autobuild+-+daffy+-+dt-core)](https://ci.duckietown.org/job/Docker%20Autobuild%20-%20daffy%20-%20dt-core/)
[![Docker Hub](https://img.shields.io/docker/pulls/duckietown/dt-core.svg)](https://hub.docker.com/r/duckietown/dt-core)


Code that runs the core stack on the Duckiebot in ROS.
