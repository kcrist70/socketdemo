#!/bin/bash
check_date=`date +"%Y-%m-%d %H:%M:%S"`
count=`ps -ef |grep yefei |grep 'python3.6 server.py' |grep -v grep|awk '{print $2}'|wc -l`
task_id=`ps -ef |grep yefei |grep 'python3.6 server.py' |grep -v grep|awk '{print $2}'`
if [[ $count == 1 ]]
then
    echo $check_date "server is running" >> monitor.log
else
    echo $task_id | while read line
    do
        kill -9 $line
    done
    nohup python3.6 /home/yefei/PhoneLogSocket/bin/server.py &
    echo $check_date "restart phonelogclient.py" >> monitor.log
fi
