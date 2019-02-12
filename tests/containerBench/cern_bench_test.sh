#install benchmarking suite: TODO using yum might fail if the architect doesn't chose centos for the VMs!
yum install -y cern-benchmark
yum install -y cern-benchmark-docker

echo "Waiting for ML results file..."

# run the tests
cern-benchmark-docker -o --benchmarks=<kv;whetstone;DB12;hyper-benchmark>



echo "ML results file fetched!"
