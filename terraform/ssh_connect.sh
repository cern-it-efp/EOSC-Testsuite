#!/bin/bash

#TODO: retry ONLY if the problem is ssh related: connection refused, broken pipe or similar, but not another one (255),
#   In case of copying a file with scp, if the file doesn't exist (useful in main.tf) it returns 1 which is the normal out error code.

#---scp specific
scp=false
source=""
destination=""

user=""
host_ip=""
file_path="" #path from where ssh_connect.sh is called, not from where ssh_connect.sh is located
options=""
hide_logs=""
retries=""

while [ "$1" != "" ]; do
    case $1 in
        --src )                 shift
                                source=$1
                                ;;
        --dst )                 shift
                                destination=$1
                                ;;
        --usr )                 shift
                                user=$1
                                ;;
        --ip )                  shift
                                host_ip=$1
                                ;;
        --file )                shift
                                file_path=$1
                                ;;
        --opts )                shift
                                options=$1
                                ;;
        --retries )             shift
                                retries="<="$1
                                ;;
        --hide-logs )           hide_logs=true
                                ;;
        --scp )                 scp=true
                                ;;
        * )                     exit 1
    esac
    shift
done


if  [[ $scp = true ]]; then
  if  [[ $hide_logs = true ]]; then
    for (( c=1; c$retries; c++ )); do command scp -o 'StrictHostKeyChecking no' $source $destination ; [ $? -eq 0 ] && break ; done &> /dev/null
  else
    for (( c=1; c$retries; c++ )); do command scp -o 'StrictHostKeyChecking no' $source $destination ; [ $? -eq 0 ] && break ; done
  fi
else
  if  [[ $hide_logs = true ]]; then
    for (( c=1; c$retries; c++ )); do command ssh -o 'StrictHostKeyChecking no' $user@$host_ip 'bash -s' -- < $file_path $options ; [ $? -eq 0 ] && break ; done &> /dev/null
  else
    for (( c=1; c$retries; c++ )); do command ssh -o 'StrictHostKeyChecking no' $user@$host_ip 'bash -s' -- < $file_path $options ; [ $? -eq 0 ] && break ; done
  fi
fi
