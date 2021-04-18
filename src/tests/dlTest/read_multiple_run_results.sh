#!/bin/bash

# cd into the provider's results folder
for f in $(ls) ; do
	echo ""
	echo "---------------------------------------------------"
	echo Run: $f
	cat $f/general.json | jq .testsCatalog.dlTest.nodes ;
	cat $f/general.json | jq .testsCatalog.dlTest.flavor ;
	cat $f/detailed/bb_train_history.json | jq .train_time ;
done
