7. Cost of run calculation
---------------------------------------------

An approximative cost of running the test-suite will be calculated in case the prices are specified at configs.yaml under the *costCalculation* section.
In this configuration file, one must specify the price per hour for the different resources:

+-----------------------+---------------------------------------------------------------------------------------------------------+
| Name	                | Explanation / Values                                                                                    |
+=======================+=========================================================================================================+
|generalInstancePrice   | Price per hour of VM with the flavor chosen for the general cluster.                                    |
+-----------------------+---------------------------------------------------------------------------------------------------------+
|GPUInstancePrice       | Price per hour of VM with the flavor chosen for the GPU cluster.                                        |
+-----------------------+---------------------------------------------------------------------------------------------------------+
|HPCInstancePrice       | Price per hour of VM with the flavor chosen for the HPC cluster.                                        |
+-----------------------+---------------------------------------------------------------------------------------------------------+
|s3bucketPrice          | S3 bucket price.                                                                                        |
+-----------------------+---------------------------------------------------------------------------------------------------------+

If a price value is required for the cost calculation but the *costCalculation* section is not properly filled (For example, S3 Endpoint test was set to True
but *s3bucketPrice* was not set), no approximation will be given at all.

At the end of the run, the resulting approximated cost will be added to the file containing general test suit run results.
In case this information isn't needed, simply leave the values on the section *costCalculation* empty.
Note that this is a cost estimate and not an exact price.

The formula used is as follows:

*(Number of VMs created) x (Price of a VM per hour) x (Time in hours the VMs were used for the test-suite run) + (Cost of other resources)*

Where "Cost of other resources" are the cost of resources which are not simple compute, like storage. For example in the case of the S3 Endpoint test:

*(Price of a S3 bucket per hour) x (Time in hours the bucket was used for the test)*

Note that the price per request or data amount (GB) are not considered here as these are not significant since less than 10 requests are done for this test and for very small data sets.
Note also that only the cost of the running time of the VM is considered, so if your provider charges for VM creation and not only for the time it is running, the cost obtained will vary to the real one.
