6. Results
---------------------------------------------
Once all the selected tests finish the run, the test-suite has completed its execution. The results and logs of the validation exercise can be seen inside *EOSC-Testsuite/results* (JSON format).
Prior to completing the runs, a message will be printed to the console showing the exact path to the results. There you will find a file *general.json* containing general
details, estimated cost and brief test results information and also a directory *detailed* containing more detailed information for each test.

Upload results to CERN's S3
==============================

Prior to the run, define the environment variables ``S3_ACC_KEY`` and ``S3_SEC_KEY`` and later use the option *--publish*. The results of the run should be on the bucket after the run completes.
