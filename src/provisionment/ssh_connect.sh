#!/bin/bash

#---scp specific
scp=false
source=""
destination=""

user=""
host_ip=""
file_path="" #path from where ssh_connect.sh is called, not from where ssh_connect.sh is located
options=""
hide_logs=false
retries=""
key=""

while [ "$1" != "" ]; do
  case $1 in
    --key )                 shift
      key="-i "$1
      ;;
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
    for (( c=1; c$retries; c++ )); do
      command scp $key -o 'StrictHostKeyChecking no' $source $destination
      if [ $? -eq 0 ]; then
        success=0
        break
      else
        success=1
      fi
    done &> /dev/null
  else
    for (( c=1; c$retries; c++ )); do
      command scp $key -o 'StrictHostKeyChecking no' $source $destination
      if [ $? -eq 0 ]; then
        success=0
        break
      else
        echo "Failed connection..."
        success=1
      fi
    done
  fi
else
  if  [[ $hide_logs = true ]]; then
    for (( c=1; c$retries; c++ )); do
      command ssh $key -o 'StrictHostKeyChecking no' $user@$host_ip 'bash -s' -- < $file_path $options
      if [ $? -eq 0 ]; then
        success=0
        break
      else
        success=1
      fi
    done &> /dev/null
  else
    for (( c=1; c$retries; c++ )); do
      command ssh $key -o 'StrictHostKeyChecking no' $user@$host_ip 'bash -s' -- < $file_path $options
      if [ $? -eq 0 ]; then
        success=0
        break
      else
        echo "Failed connection..."
        success=1
      fi
    done
  fi
fi

if [[ $success != 0 ]]; then
  echo "ssh_connect.sh failed! IP: $host_ip"
fi

exit $success
