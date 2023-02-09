#!/usr/bin/bash

sudo rm -r eece5554 || sudo rm -r EECE5554

screen -S emulator -X quit
rm -r port_file.txt || echo "ready to roll"

cur_dir=$(pwd)

screen -S emulator -dm bash -c "echo $pwd;python3 serial_emulator.py -f gps-data.txt; echo $pwd"

sleep 3

port=$(cat port_file.txt)


git clone $1

for ((i=0;i<1;i++))
do
    
   

    cd eece5554/LAB1 || cd EECE5554/LAB1

    mkdir src

    sudo mv  gps_driver src/

    catkin_make

    source devel/setup.bash

    
    python3 $cur_dir/LAB1_ROS_Struct_Checker.py $i $port

    cd $cur_dir


done

screen -S emulator -X quit

rm -r port_file.txt