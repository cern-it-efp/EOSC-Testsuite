#!/bin/bash


#1) At the commissioning of the link at to ensure full capacity is available. Run a couple of manual perfSONAR tests with either single or multi stream iperf3 - single
#stream should get at least 40% of capacity, multi stream should reach at least 80%. This assumes 10Gbps link and bare metal perfSONAR box at the contractor's DC with 10Gbps NIC.

#2) Regular testing of throughput during normal usage with at least 5-10% of capacity on average to prevent that the link stops performing and drops to Mbits or Kbits.

pscheduler task throughput --dest hostname
pscheduler ping hostname

#Latency will be tested in both cases and depending on the placement of contractors DC get corresponding numbers: in Europe, this means one
#way delay of ~ less than 30ms, with no packet re-ordering, no duplicates and without any consistent packet loss (i.e. packet loss of more than 1%
#for more than 3 hours).
