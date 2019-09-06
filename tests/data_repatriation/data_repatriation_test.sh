#!/bin/bash

# 1) clone repo
git clone https://github.com/ignpelloz/cloud-exporter.git ; cd cloud-exporter

# 2) Modify configs.yaml
cat > configs.yaml <<EOL
access_token: $TOKEN
path_to_data: ./dir1
title: "Uploaded from Cloud Validation Test-Suite (VM on $PROVIDER)"
sandbox: False
EOL

#create folder with files to upload
mkdir -p dir1/dir2/dir3
echo "Uploaded from Cloud Validation Test-Suite" > dir1/file1
echo "Uploaded from Cloud Validation Test-Suite" > dir1/dir2/file1
echo "Uploaded from Cloud Validation Test-Suite" > dir1/dir2/dir3/file1

logs=$(./cloud-exporter.py) ; if [ $? -ne 0 ] ; then result=fail ; else result=success ; fi

#create a simple json result file
cat > "/home/data_repatriation_test.json" <<EOF
{
	"provider":"$PROVIDER",
	"result":"$result"
}
EOF

#WORKAROUND: Needed this to keep pod alive to fetch logs file
while true; do echo "keeping this alive..."; done
