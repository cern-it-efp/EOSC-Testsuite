#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *    

def cpuBenchmarkingTest(testsCatalog, configs, resDir, obtainCost):
    """Run containerised CPU Benchmarking test."""

    res = False
    testCost = 0
    testsRoot =  "tests/"
    with open(testsRoot + "cpu_benchmarking/raw/cpu_benchmarking_pod_raw.yaml",
              'r') as infile:
        with open(testsRoot + "cpu_benchmarking/cpu_benchmarking_pod.yaml",
                  'w') as outfile:
            outfile.write(infile.read().replace(
                "PROVIDER_PH", configs["providerName"]))

    if kubectl(
            Action.create,
            file="%scpu_benchmarking/cpu_benchmarking_pod.yaml" %
            testsRoot,
            toLog="logging/shared") != 0:
        writeFail(resDir, "cpu_benchmarking.json",
                  "Error deploying cpu_benchmarking_pod.", "logging/shared")
    else:
        fetchResults(
            resDir,
            "cpu-bmk-pod:/tmp/cern-benchmark_root/bmk_tmp/result_profile.json",
            "cpu_benchmarking.json",
            "logging/shared")
        # cleanup
        writeToFile("logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="cpu-bmk-pod")
        res = True

    return ({"test": "cpuBenchmarking", "deployed": res}, testCost)