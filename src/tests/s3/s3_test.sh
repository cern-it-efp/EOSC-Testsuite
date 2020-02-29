#!/bin/bash

# Some setup
bucketBase="eoscts-s3-bucket"
export bucket="s3://"$bucketBase
opts="--endpoint-url=$ENDPOINT"
fail="\e[31mFailure\e[39;49m"
succeed="\e[32mSuccess\e[39;49m"
timeout=10 # seconds
log="s3_test.json"

keepAlive () {
	#WORKAROUND: Needed this to keep pod alive to fetch logs file
	while true; do echo "keeping this alive..."; done
}

writeResult () {
	echo "{\"info\":\"$1\", \"result\":\"fail\"}" > /home/${log}
	keepAlive
}

echo "Creating bucket for testing..."
aws s3 mb ${opts} ${bucket}
if [ $? -ne 0 ]; then
	writeResult "Unable to create bucket"
fi


# Some functions

cleanup () {
	echo
	echo "Cleaning test files from bucket"
	for obj in tf01 td01/tf01 td01/; do
		if ( aws s3 ls ${opts} ${bucket}/${obj} &> /dev/null ); then
			aws s3 rm ${opts} ${bucket}/${obj}
		fi
	done
	echo
}

test_start () {
	echo $testinfo
	exec 3>&1
	exec 4>&2
	exec 1> ${tdir}/stdout
	exec 2> ${tdir}/stderr
	set -xv
}

close_item(){
	if [ "$testinfo" == "Checking Directory Creation" ]; then
		echo "		}" >> ${log}
	else
		echo "		}," >> ${log}
	fi
}

test_end() {
	set +xv
	exec 1>&3
	exec 2>&4
	#cat ${tdir}/stdout >> ${log}
	echo "		{"  >> ${log}
	echo "			\"tittle\":\"$testinfo\","  >> ${log}
	#echo "STDERR" >> ${log}
	echo "			\"logs\":\"$(sed -e "s/${AWS_SECRET_ACCESS_KEY}/\${AWS_SECRET_ACCESS_KEY}/g" ${tdir}/stderr)\"," >> ${log}
	if [ $1 -ne 0 ]; then
		echo -e $fail
		echo "			\"result\":\"Failure\"" >> ${log}
		close_item
		return 1
	else
		echo -e $succeed
		echo "			\"result\":\"Success\"" >> ${log}
		close_item
		return 0
	fi
}

if [ -f ${log} ]; then
	rm ${log}
fi
echo "{" >> ${log}
echo "	\"results\":[" >> ${log}

# Create a temp directory for uploads and downloads
tdir=`mktemp -d`

echo "Starting to test ${bucket}"
echo

# Do we have access?
testinfo="Checking Access"
test_start
timeout ${timeout} aws s3 ls ${opts} ${bucket}
test_end $?
if [ $? -ne 0 ]; then
	writeResult "No access to bucket, quitting"
	rm -rf ${tdir}
fi

# Create a test file
#size=2048 # blocks
size=16 # blocks
dd if=/dev/urandom of=${tdir}/1M count=${size} 2> /dev/null
echo MARK01 | dd seek=4 of=${tdir}/1M conv=notrunc 2> /dev/null
echo MARK02 | dd seek=8 of=${tdir}/1M conv=notrunc 2> /dev/null

# Clean up the bucket
cleanup

# Start testing

# Can we put?
testinfo="Trying PUT"
test_start
timeout ${timeout} aws s3 cp ${opts} ${tdir}/1M ${bucket}/tf01
test_end $?
if [ $? -ne 0 ]; then
	writeResult "Can't put, quitting"
	rm -rf ${tdir}
fi
testinfo="Checking PUT"
test_start
timeout ${timeout} aws s3 ls ${opts} ${bucket}/tf01
test_end $?
echo

# Can we get?
testinfo="Trying GET"
test_start
timeout ${timeout} aws s3 cp ${opts} ${bucket}/tf01 ${tdir}/1M.get
test_end $?
testinfo="Checking GET"
test_start
diff ${tdir}/1M ${tdir}/1M.get
test_end $?
echo

# Can we get a byte range?
testinfo="Trying Range request 1"
test_start
timeout ${timeout} aws s3api get-object ${opts} --bucket $bucketBase --key tf01 --range bytes=2048-2053 ${tdir}/1M.get.r1
test_end $?
testinfo="Checking Range request"
test_start
cat ${tdir}/1M.get.r1 && echo
test `cat ${tdir}/1M.get.r1` == 'MARK01'
test_end $?

testinfo="Trying Range request 2"
test_start
timeout ${timeout} aws s3api get-object ${opts} --bucket $bucketBase --key tf01 --range bytes=4096-4101 ${tdir}/1M.get.r2
test_end $?
testinfo="Checking Range request"
test_start
cat ${tdir}/1M.get.r2 && echo
test `cat ${tdir}/1M.get.r2` == 'MARK02'
test_end $?
echo

# Can we get a double byte range?
testinfo="Trying double range request"
test_start
timeout ${timeout} aws s3api get-object ${opts} --bucket $bucketBase --key tf01 --range bytes=2048-2054,4096-4101 ${tdir}/1M.get.rr
test_end $?
testinfo="Checking first chunk"
test_start
# Check mark is there, and we didn't just get the whole file
grep -q MARK01 ${tdir}/1M.get.rr && ! diff ${tdir}/1M ${tdir}/1M.get.rr
test_end $?
testinfo="Checking second chunk"
test_start
# Check mark is there, and we didn't just get the whole file
grep -q MARK02 ${tdir}/1M.get.rr && ! diff ${tdir}/1M ${tdir}/1M.get.rr
test_end $?
echo

# Can we delete?
testinfo="Trying Delete"
test_start
timeout ${timeout} aws s3 rm ${opts} ${bucket}/tf01
test_end $?
echo

# Can we create a dir?
testinfo="Trying Directory Creation"
test_start
timeout ${timeout} aws s3 cp ${opts} ${tdir}/1M ${bucket}/td01/tf01
test_end $?
testinfo="Checking Directory Creation"
test_start
out=`aws s3 ls ${opts} ${bucket}/td01 | awk '{print $NF}'`
#[ x${out} = 'xtf01' ] If this wants to be seen, then '/' should be appended at the end of the path for the command
[ ${out} = 'td01/' ]
test_end $?

# Clean up
rm -rf ${tdir}
cleanup

# 3) Delete created bucket
echo "Deleting test bucket..."
aws s3 rb ${opts} ${bucket}

echo "	]" >> ${log}
echo "}" >> ${log}
cp ${log} /home/${log}

keepAlive
