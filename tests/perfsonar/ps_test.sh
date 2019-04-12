#!/bin/bash

#FUNCTIONS

notAlive(){
  echo "{\"info\":\"pScheduler endpoint not reachable.\", \"result\":\"fail\"}" >> /tmp/perfsonar_test.json;
  exit 1
}

throughputTest(){
  out=$(pscheduler task --format=json throughput --dest $ENDPOINT)
  while [ $? != 0 ]
  do out=$(pscheduler task --format=json throughput --dest $ENDPOINT)
  done
  echo "{\"throughput\": ${out}, " >> /tmp/perfsonar_test.json;
}

rttTest(){
  out=$(pscheduler task --format=json rtt --dest $ENDPOINT)
  while [ $? != 0 ]
  do out=$(pscheduler task --format=json rtt --dest $ENDPOINT)
  done
  echo "\"rtt\": ${out}, " >> /tmp/perfsonar_test.json;
}

traceTest(){
  out=$(pscheduler task --format=json trace --dest $ENDPOINT)
  while [ $? != 0 ]
  do out=$(pscheduler task --format=json trace --dest $ENDPOINT)
  done
  echo "\"trace\": ${out}, " >> /tmp/perfsonar_test.json;
}

latencyTest(){
  #pscheduler task --format=json latencybg --packet-count 38 --dest $ENDPOINT
  out=$(pscheduler task --format=json latency --dest $ENDPOINT)
  while [ $? != 0 ]
  do out=$(pscheduler task --format=json latency --dest $ENDPOINT)
  done
  echo "\"latency\": ${out}}" >> /tmp/perfsonar_test.json;
}

#START TESTING

pscheduler ping $ENDPOINT || notAlive # if host not reachable, exit

throughputTest &> /dev/null
rttTest &> /dev/null
traceTest &> /dev/null
latencyTest &> /dev/null

sed 's/No further runs scheduled.//g' /tmp/perfsonar_test.json > /tmp/perfsonar_results_raw.json
sed 's/\\n//g' /tmp/perfsonar_results_raw.json > /tmp/perfsonar_results_raw1.json
sed 's/\\t//g' /tmp/perfsonar_results_raw1.json > /tmp/perfsonar_results_raw2.json
sed 's/\\//g' /tmp/perfsonar_results_raw2.json > /tmp/perfsonar_results_raw3.json
awk 'NF' /tmp/perfsonar_results_raw3.json > /tmp/perfsonar_results.json
