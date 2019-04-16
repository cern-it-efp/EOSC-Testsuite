1. Getting started
---------------------------------------------
Please follow the steps below in order to deploy and test a cloud provider:

1.1 Install Terraform
==========================
Terraform is the tool that creates the VMs that will later become a Kubernetes cluster. The test-suite makes use of it so download and
install `Terraform <https://learn.hashicorp.com/terraform/getting-started/install.html>`_ on your machine.
In some cases, providers are not fully supported by Terraform, however they might provide plugins to bridge this gap. In such cases, please refer to the documentation of the provider to download the plugin. 
Once downloaded, this must be placed at *~/.terraform.d/plugins* and execution permissions must be given to it (*+x*).

1.2 Manage ssh keys
==========================
A ssh key pair is needed to establish connections to the VMs to be created later. Therefore, you must create (or import) this key on your provider beforehand and place the private key at *~/.ssh/id_rsa*. Note errors may occur if your key doesn't have the right permissions. Set these to the right value using the following command:

.. code-block:: console

    $ chmod 600 path/to/key

1.3 Dependencies
==========================
This test-suite requires some packages to work properly and these must be installed by yourself directly. Please see below.

Kubernetes client
^^^^^^^^^^^^^^^^^^^^^
In order to manage the Kubernetes cluster locally instead of using the master node, install `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_ on your machine.

Python
^^^^^^^^^
Version python3 is required. In some Linux distributions, it has been noticed that not all the python required packages are included by default, like pyyaml.
In such cases, please install the missing packages according to the error messages when running the Test-Suite.


1.4 Download and preparation
==========================================
Cloning repository
^^^^^^^^^^^^^^^^^^^^^^^
Please clone the repository as follows and cd into it:

.. code-block:: console

    $ git clone https://github.com/cern-it-efp/OCRE-Testsuite.git
    $ cd OCRE-Testsuite

Configuration
^^^^^^^^^^^^^^^^^^^^^^^^
While completing this task, please refer to `Terraform's documentation <https://www.terraform.io/docs/providers/>`_ in order to complete it successfully as some parts are provider specific and differ from one provider to another.
You will find at the root of the cloned repository a file named *configs_raw.yaml*. You must rename it *configs.yaml* and fill it to match your requirements. **A filled example can be
found in */config_examples***. This file contains different sections:

``general``

For specifying general variables:

+-----------------------+------------------------------------------------------------------------------------+
| Name	                | Explanation / Values                                                               |
+=======================+====================================================================================+
|clusterNodes           | Indicate the number of nodes the cluster must contain, including master node.      |
+-----------------------+------------------------------------------------------------------------------------+
|providerName           | Name of the provider for Terraform.                                                |
+-----------------------+------------------------------------------------------------------------------------+
|providerInstanceName   | Compute instance name for Terraform. This is provider specific.                    |
+-----------------------+------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key                                           |
+-----------------------+------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                      |
+-----------------------+------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                  |
+-----------------------+------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                     |
+-----------------------+------------------------------------------------------------------------------------+

Note that it's possible to choose between "Docker Community Edition" and "Docker Engine" (older Docker packages). However it's **highly recommended** to leave these variables empty to create a cluster with the latest stack.

``auth``

For specifying the credentials to connect to the provider and deploy resources.

+-------------+----------------------------------------------------------------------------------------------+
| Name	      | VAccepted Values                                                                             |
+=============+==============================================================================================+
|useFile      | Indicate if a credentials file is used instead of secret-key pair (Boolean). Required.       |
+-------------+----------------------------------------------------------------------------------------------+
|credentials  | String block with the required credentials.                                                  | 
|             | | This is not yaml but string, therefore use '=' and ' " '. (cloud provider specific).       |
+-------------+----------------------------------------------------------------------------------------------+

``instanceDefinition``

In this section you should write all the key-pair values that would be written on the body of an instance declaration resource on Terraform, according to the cloud you want to test.
Refer to the documentation of the cloud provider to check which pairs you need to specify. In any case, you can run the Test-Suite (next steps) and if there is any missing pair a message will be shown in the terminal telling you which ones are these. This is how you must specify each pair::

  <YOUR_PROVIDER'S_STRING_FOR_A_KEY> = "<VALUE_GIVEN_FOR_THAT_KEY>"

An example (Exoscale cloud provider)::

  display_name = "kubenode"#NAME
  template = "Linux CentOS 7.5 64-bit"
  size = "Medium"
  key_pair = "k_cl"
  security_groups = ["kgroup"]
  disk_size = 50
  zone = "ch-gva-2"

Please pay attention in this section to the name for the instance. A random string will be added later to the name given to the instance in order to avoid DNS issues when running the test-suite several times. To achieve this, the block must contain the '#NAME' placeholder. When specifying the name for the instance, please follow this structure::

  <YOUR_PROVIDER'S_STRING_FOR_NAME> = "<NAME_FOR_YOUR_INSTANCES>"#NAME

Now, lets image you provider's string for the instance name is "display_name", and you want to call your instances "kubenode" then you should write::

  display_name = "kubenode"#NAME

Note the '#NAME'!

| [**NOTE 1**: Even though this is a yaml file, '=' is used on this section instead of ':' as that's required by Terraform files and this will be taken as a whole block and placed directly on a .tf file]
| [**NOTE 2**: Clouds that don't support resource creation with Terraform or k8saaS can't currently be tested with this Test-Suite]
|
Tests Catalog
^^^^^^^^^^^^^^^^^^^

In the section ``testsCatalog`` of *configs.yaml*, you have to specify which tests you want to run. If you want to run a certain test simply set its *run* variable to the True Boolean value. On the other hand, if you don't want it to be run set this value to False. Please find below, a description of each test that has already been integrated in the Test-Suite:

**Deep Learning using GPUs: It trains a Generative Adversarial Network (GAN) using a Kubernetes cluster (GPU flavored) with Kubeflow and MPI.**

Note that for this test a cluster with GPU flavor is required.
For this test, apart from the *run* variable, the following can be set in the configs.yaml file:

+--------------+----------------------------------------------------------------------------------------------------------------+
|Name	       | Explanation / Values                                                                                           |
+==============+================================================================================================================+
|nodes         | Number of nodes to be used for the deployment. If not set, the max number of nodes available will be used.     |
+--------------+----------------------------------------------------------------------------------------------------------------+

This test is currently undergoing development and testing, hence it can't be fully deployed.

- Contributors/owners: Sofia Vallecorsa (CERN) - sofia.vallecorsa@cern.ch; Jean-Roch Vlimant (Caltech)
- Repository: https://github.com/svalleco/mpi_learn
|
**S3 endpoint tests: A simple S3 test script to test functionality of S3-like endpoints, checking the following:**

S3 authentication (access key + secret key, PUT, GET, GET with prefix matching, GET chunk, GET multiple chunks
|
For this test, apart from the *run* variable, the following ones must be set on the configs.yaml file:

+----------------+----------------------------------------------------------------------------------------------------------------+
| Name	         | Explanation / Values                                                                                           |
+================+================================================================================================================+
|endpoint        | Endpoint under which your S3 bucket is reachable. This URL must not include the bucket name but only the host. |
+----------------+----------------------------------------------------------------------------------------------------------------+
|accessKey       | Access key for S3 resource management.                                                                         |
+----------------+----------------------------------------------------------------------------------------------------------------+
|secretKey       | Secret key for S3 resource management.                                                                         |
+----------------+----------------------------------------------------------------------------------------------------------------+

- Contributors/Owners: Oliver Keeble (CERN) - oliver.keeble@cern.ch
- Repository: https://gitlab.cern.ch/okeeble/s3test

|

**Data Export: Move data from a VM running on a cloud provider to Zenodo.**

When using cloud credits, when credit is exhausted cloud, data can be repatriated or moved to a long-term data storage service. The example used in this test uses Zenodo service maintained by CERN: https://zenodo.org/, verifying that the output data can be taken from the cloud provider to Zenodo.

Contributors/owners: Ignacio Peluaga - ignacio.peluaga.lozada@cern.ch
Repository: https://github.com/ignpelloz/cloud-exporter

|

**CPU Benchmarking: Containerised benchmarking tools.**

Suite contanining several CPU benchmarks used at CERN.
The following benchmarks are run on the cloud provider, using a containerised approach:

- DIRAC Benchmark
- ATLAS Kit Validation
- Whetstone: from the UnixBench benchmark suite.
- Hyper-benchmark: A pre-defined sequence of measurements and fast benchmarks.

Contributors/Owners: Domenico Giordano (CERN) - domenico.giordano@cern.ch
Repository:  https://gitlab.cern.ch/cloud-infrastructure/cloud-benchmark-suite 

|

**perfSONAR: Networking performance measurements.**

perfSONAR is a network measurement toolkit designed to provide federated coverage of paths, and help to establish end-to-end usage expectations.

In this test, a perfSONAR testpoint is created using a containerised approach on the cloud provider infrastructure. 
The following tests are launched end to end:

- throughput: A test to measure the observed speed of a data transfer and associated statistics between two endpoints.
- rtt: Measure the round trip time and related statistics between hosts.
- trace: Trace the path between IP hosts.
- latencybg: Continuously measure one-way latency and associated statistics between hosts and report back results periodically.

The endpoint for these tests must be specified at configs' *endpoint* variable. Use endpoints from:

- `List of throughput hosts <https://fasterdata.es.net/performance-testing/perfsonar/esnet-perfsonar-services/esnet-iperf-hosts/>`_
- `perfSONAR Toolkit <http://perfsonar-otc.hnsc.otc-service.com/toolkit/>`_
- `Lookup Services Directory <http://stats.es.net/ServicesDirectory/>`_

Contributors/Owners: Shawn Mckee (University of Michigan) - smckee@umich.edu; Marian Babik CERN) - marian.babik@cern.ch
Repository: https://github.com/perfsonar/perfsonar-testpoint-docker

|

**FDMNES: Simulation of X-ray spectroscopies.**

The aim of the FDMNES project is to supply to the community a user friendly code to simulate x-ray spectroscopies, linked to the real absorption (XANES, XMCD) or resonant scattering (RXD in bulk or SRXRD for surfaces) of the synchrotron radiation.
IT uses parallel calculations using OpenMPI. As an HPC test FDMNES is rather heavy on CPU and Memory and light on I/O.

This test is currently under development and will be available on the next release of the Test-Suite.

Contributors/Owners: Rainer Wilcke (ESRF) - wilcke@esrf.fr
Repository: http://neel.cnrs.fr/spip.php?article3137&lang=en

|

[**NOTE**: If no test's *run* is set to True, this tool will simply create a raw Kubernetes cluster]

|

1.5 Run the test-suite
========================
Once the previous steps are completed, the Test-Suite is ready to be run:

.. code-block:: console

    $ ./test_suite.py <options>

Terraform will first show the user what will be done and what to create. If agreed, type "yes" and press enter.

Options
^^^^^^^^^
The following table describes all the available options:

+------------------+------------------------------------------------------------------------------------------------------------------+
| Name	           | Explanation / Values                                                                                             |
+==================+=======================================================================================================================================================+
|--only-test       | Run without creating the infrastructure (VMs and cluster), only deploy tests. Not valid for the first run.                                            |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
|--auto-retry      | Automatically retry in case of errors on the Terraform phase. Note that in the case errors occur, the user will have to stop the run using Ctrl+Z.    |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
|--via-backend     | Runs the Test-Suite using CERN's backend service instead of the cloned local version. This option must be used for verification purposes (2nd or later runs).  |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
