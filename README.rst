===============================================================
OCRE Test-Suite for cloud provider validation - CERN IT (EFP)
===============================================================

This tool is intended to be used for cloud providers (public cloud) validation and testing. The test-suite does 4 main things:

1) Infrastructure provisioning: VMs are created using Terraform and then Kubernetes and Docker are installed on them to create a k8s cluster.

2) Deploy the tests: Kubernetes resource definition files (YAML) are used to deploy the tests, either as single pods or deployments.

3) Harvest results: at the end of each test run a result file -written in JSON- is created. This file is stored locally.

4) Through the verification system, the TS is triggered from a service running at CERN. In this case results are then pushed to a S3 Bucket at CERN.

The test set here available is the one used for `EC project Helix Nebula The Science Cloud <https://www.hnscicloud.eu/>`_.

**This test-suite has been tested on:**

| Python: 3
| Linux distros: Ubuntu, Centos, Coreos, Debian, RedHat, Fedora
| OS running on provider's VMs : Centos
| Providers:  Exoscale (Cloudstack), CERN Private Cloud (OpenStack), Cloudscale (OpenStack)


*****

1. Getting started
---------------------------------------------
Follow these steps to test a cloud provider:

1.1 Install Terraform
==========================
Terraform is the tool that creates the VMs that will later become a Kubernetes cluster. The test-suite makes use of it so download and
install `Terraform <https://learn.hashicorp.com/terraform/getting-started/install.html>`_ on your machine.
In some cases, providers are not fully supported by Terraform but these provide plugins to gap this bridge. In such cases, refer to the documentation of the provider
to download the plugin. Once downloaded, this must be placed at *~/.terraform.d/plugins* and execution permissions must be given to it (*+x*).

1.2 Manage ssh keys
==========================
A ssh key pair is needed to establish connections to the VMs that will be created later. Therefore you must create (or import) this key on your provider beforehand
and place the private key at *~/.ssh/id_rsa*. Note errors may occur if your key doesn't have the right permissions. Set these to the right value using the following command:

.. code-block:: console

    $ chmod 600 path/to/key


1.3 Dependencies
==========================
This test-suite requires some packages to work properly and these must be installed by yourself.

Kubernetes client
^^^^^^^^^^^^^^^^^^^^^
In order to manage the Kubernetes cluster locally instead of using the master node, install `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_ on your machine.

Python
^^^^^^^^^
Version python3 is required. In some Linux distributions, it has been seen not all the python required packages are included by default, like pyyaml.
In such cases, install the missing packages according to the error messages when running the test-suite.


1.4 Download and preparation
==========================================
Clone repository
^^^^^^^^^^^^^^^^^^^^^^^
Clone this repository as follows and cd into it:

.. code-block:: console

    $ git clone https://github.com/cern-it-efp/OCRE-Testsuite.git
    $ cd OCRE-Testsuite

Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
While completing this task refer to `Terraform's documentation <https://www.terraform.io/docs/providers/>`_ in order to complete it successfully as some parts are provider
specific and differ from one provider to another.
You will find on the root of the cloned repository a file named *configs_raw.yaml*. You must rename it *configs.yaml* and fill it to match your requirements. **A filled example can be
found in */config_examples***. This file has different sections:

``general``

For specifying general variables:

+-----------------------+-------------------------------------------------------------------------------------+
| Name	                | Explanation / Values                                                                |
+=======================+=====================================================================================+
|clusterNodes           | Indicate the number of nodes the cluster must contain, including master node.       |
+-----------------------+-------------------------------------------------------------------------------------+
|providerName           | Name of the provider for Terraform.                                                 |
+-----------------------+-------------------------------------------------------------------------------------+
|providerInstanceName   | Compute instance name for Terraform. This is provider specific.                     |
+-----------------------+-------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key                                            |
+-----------------------+-------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                       |
+-----------------------+-------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                   |
+-----------------------+-------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                      |
+-----------------------+-------------------------------------------------------------------------------------+

Note that it's possible to chose between Docker Community Edition and Docker Engine (older Docker packages), however it is **highly recommended** to leave these variables empty to create a
cluster with the latest stack.

``auth``

For specifying the credentials to connect to the provider and deploy resources.

+-------------+---------------------------------------------------------------------------------------------------------------------------------+
| Name	      | Explanation / Values                                                                                                            |
+=============+=================================================================================================================================+
|useFile      | Indicate if a credentials file is used instead of secret-key pair (Boolean). Required property.                                 |
+-------------+---------------------------------------------------------------------------------------------------------------------------------+
|credentials  | String block containing the required credentials. This is not yaml but string, therefore use '=' and ' " '. (Provider specific).|
+-------------+---------------------------------------------------------------------------------------------------------------------------------+

``instanceDefinition``

In this section you should write all the key-pair values that would be written on the body of an instance declaration resource on Terraform, according to the provider you want to test.
Refer to the documentation of the provider to check which pairs you need to specify and in any case you can run the test-suite (next steps) and if there is any missing pair a message
will be shown on the terminal telling you which ones these are. This is how you must specify each pair::

  <YOUR_PROVIDER'S_STRING_FOR_A_KEY> = "<VALUE_GIVEN_FOR_THAT_KEY>"

An example (Exoscale)::

  display_name = "kubenode"#NAME
  template = "Linux CentOS 7.5 64-bit"
  size = "Medium"
  key_pair = "k_cl"
  security_groups = ["kgroup"]
  disk_size = 50
  zone = "ch-gva-2"

Pay attention on this section to the name for the instance. A random string will be added later to the name given to the instance in order to avoid DNS issues when running
the test-suite several times. For this, the block must contain the '#NAME' placeholder. When specifying the name for the instance, follow this structure::

  <YOUR_PROVIDER'S_STRING_FOR_NAME> = "<NAME_FOR_YOUR_INSTANCES>"#NAME

So lets image you provider's string for the instance name is "display_name", and you want to call your instances "kubenode" then you should write::

  display_name = "kubenode"#NAME

Note the '#NAME'!

| [**NOTE**: Even though this is a yaml file, '=' is used on this section instead of ':' as that is required on Terraform files and this will be taken as a whole block and placed directly on a .tf file]
| [**NOTE2**: providers that do not support resource creation with Terraform or k8saaS can't be tested with this test-suite currently]
|

``testsCatalog``

In this section, you have to specify which tests you want to run. If you want to run certain test simply set its *run* variable to the True Boolean value. On the other
hand if you don't want it to be run set this value to False. Following find a description of each test:

**Deep Learning using GPU: trains a GAN making use of a Kubernetes cluster (GPU flavored) with Kubeflow and MPI.**

Note that for this test a cluster with GPU flavor is required.
For this test, besides the *run* variable, the following one can be set on the configs.yaml file:

+--------------+----------------------------------------------------------------------------------------------------------------+
| Name	       | Explanation / Values                                                                                           |
+==============+================================================================================================================+
|nodes         | Number of nodes to be used for the deployment. If not set, the max number of nodes available will be used.     |
+--------------+----------------------------------------------------------------------------------------------------------------+

Currently this test is still undergoing development and testing, hence it cant be deployed.

(Contributor/owner: Sofia Vallecorsa - sofia.vallecorsa@cern.ch)

|

**S3 endpoint tests: An S3 test script that will check the following things:**

- S3 authentication (access key + secret key)
- PUT
- GET
- GET with prefix matching
- GET chunk
- GET multiple chunks

For this test, besides the *run* variable, the following ones must be set on the configs.yaml file:

+----------------+----------------------------------------------------------------------------------------------------------------+
| Name	         | Explanation / Values                                                                                           |
+================+================================================================================================================+
|endpoint        | Endpoint under which your S3 bucket is reachable. This URL must not include the bucket name but only the host. |
+----------------+----------------------------------------------------------------------------------------------------------------+
|accessKey       | Access key for S3 resource management.                                                                         |
+----------------+----------------------------------------------------------------------------------------------------------------+
|secretKey       | Secret key for S3 resource management.                                                                         |
+----------------+----------------------------------------------------------------------------------------------------------------+

(Contributor/owner: Oliver Keeble - oliver.keeble@cern.ch)

|

**Data repatriation test: Take data from a VM running on a cloud provider to Zenodo.**

In the chase of making the scientific community embrace a vouchers usage of cloud computing, there is always a drawback: once my
cloud credits are over, what can I do with the data I have on the cloud? Zenodo is a tool developed by CERN useful in this case as it
keeps data for the long term and it is free. What this test does is to verify that data can be taken from the private cloud being tested onto Zenodo.

(Contributor/owner: Ignacio Peluaga - ignacio.peluaga.lozada@cern.ch)

|

**CPU Benchmarking: Containerised benchmarking tools.**

The following benchmarks are run on the provider side using a containerised approach:

- DIRAC Benchmark
- ATLAS Kit Validation
- Whetstone: from the UnixBench benchmark suite.
- Hyper-benchmark: A pre-defined sequence of measurements and fast benchmarks.

(Contributor/owner: Domenico Giordano - domenico.giordano@cern.ch)

|

**perfSONAR: Networking performance measurements.**

A perfSONAR testpoint is created using a containerised approach on the provider side. The following tests are launched from there to the endpoint provided by the user:

- throughput: A test to measure the observed speed of a data transfer and associated statistics between two endpoints.
- rtt: Measure the round trip time and related statistics between hosts.
- trace: Trace the path between IP hosts.
- latencybg: Continuously measure one-way latency and associated statistics between hosts and report back results periodically.

The endpoint for these tests must be specified at configs' *endpoint* variable. Use endpoints from:

- `Here <https://fasterdata.es.net/performance-testing/perfsonar/esnet-perfsonar-services/esnet-iperf-hosts/>`_
- `Here <http://perfsonar-otc.hnsc.otc-service.com/toolkit/>`_
- `Here <http://stats.es.net/ServicesDirectory/>`_

(Contributor/owner: Marian Babik - marian.babik@cern.ch)

|

**HPC test: ESRF's FDMNES: Simulation of x-ray spectroscopies.**

Parallel calculations on Linux using OpenMPI. Rather heavy on CPU and memory, light on IO.
This test is still under development and will be available on next releases.

(Contributor/owner: Rainer Wilcke - wilcke@esrf.fr)

|

[**NOTE**: If no test's *run* is set to True, this tool will simply create a raw Kubernetes cluster]

|

``costCalculation``

Fill in this section in case you would like to get an approximation of the cost of running the test-suite.

+----------------+----------------------------------------------------------------------------------------------------------------+
| Name	         | Explanation / Values                                                                                           |
+================+================================================================================================================+
|instancePrice   | Price of a VM per hour.                                                                                        |
+----------------+----------------------------------------------------------------------------------------------------------------+
|s3bucketPrice   | S3 bucket price.                                                                                               |
+----------------+----------------------------------------------------------------------------------------------------------------+

Note that if a price is required for the cost calculation but the *costCalculation* section is not properly filled (For example, S3 Endpoint test was set
to True but *s3bucketPrice* was not set), no approximation will be given.


1.5 Run the test-suite
========================
Once all the previous steps are completed, the test-suite is ready to be run:

.. code-block:: console

    $ ./test_suite.py <options>

Terraform will first show the user what it is going to do, what to create. If agreed, type "yes" and press enter.

Options
^^^^^^^^^
The following table describes all the accepted options:

+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| Name	           | Explanation / Values                                                                                                                                  |
+==================+=======================================================================================================================================================+
|--only-test       | Run without creating the infrastructure (VMs and cluster), only deploy tests. Not valid for the first run.                                            |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
|--auto-retry      | Automatically retry in case of errors on the Terraform phase. Note that in the case errors occur, the user will have to stop the run using Ctrl+z.    |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
|--via-backend     | Runs the Test-Suite using CERN's backend service instead of the cloned local version. This option must be used for verification (2nd or later runs).  |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+


2. Using existing clusters
---------------------------------------------
It is also possible to use this tool for testing providers that support Kubernetes as a Service. This is, the provider offers the user a way for simply creating a cluster.
In case you want to validate a provider that offers this and want to take advantage of it, simply skip steps 1.1 and 1.2 (install Terraform and manage ssh keys) and when
running the test-suite, use option *--only-test* for normal -local results- run and *--via-backend* for verification runs. **Note that you must have the file *~/.kube/config*
for the previously provisioned cluster on your local machine so that it can be managed from there.**


3. Results
---------------------------------------------
Once all tests are run and the test-suite has completed its execution, the results and logs of this cloud benchmarking can be seen at /results in JSON format.
Prior to completing the run, a message will be printed to the console showing the exact path to the results. There you will find a file *general.json* containing general information
such as IPs of the provisioned VMs, estimated cost and brief test results information and also a directory *detailed* containing more detailed information for each test.


4. Verification
---------------------------------------------
Run using *--via-backend* so that the proxy at CERN runs the TS (only deploys tests, no provisioning), harvests results and push them to CERN's S3 bucket.
Before starting the run, a message will be shown asking for yes/no answer. It warns the user that backend runs publish results to the CERN bucket.
**Note that this feature is still under development and testing and will be available on next releases.**


5. Cost of run calculation
---------------------------------------------
An approximation of the cost of running the test-suite will be calculated in case the prices are specified at configs.yaml under the *costCalculation* section.
There you must specify the price per hour for each resource and at the end of the run, the resulting approximated cost will be added to the results json file.
In case you do not want this information, simply leave the values on the section *costCalculation* empty.
Note that this is an approximation and not an exact value. Therefore the value provided here might vary to the real one.
The formula used is as follows:

*(Number of VMs created) x (Price of a VM per hour) x (Time in hours the VMs were used for the test-suite run) + (Cost of other resources)*

Where "Cost of other resources" are the cost of resources which are not compute resources, like storage. For example in the case of the S3 Endpoint test:

*(Price of a S3 bucket per hour) x (Time in hours the bucket was used for the test)*

Note that the price per request or data amount (GB) are not considered here as these are not significant since less than 10 requests are done for this test and for very small data sets.
Note also that here only the cost of the running time of the VM is considered, so if your provider charges also for creating a VM and not only for the time it is running, the cost
here obtained will vary to the real one.

6. License
---------------------------------------------
Copyright (C) CERN.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see `gnu.org/licenses <https://www.gnu.org/licenses/>`_.

.. image:: img/logo.jpg
   :height: 20px
   :width: 20px
   :scale: 20
   :target: https://home.cern/
   :alt: CERN logo
