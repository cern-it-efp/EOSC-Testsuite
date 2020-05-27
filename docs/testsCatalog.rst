2. Tests Catalog
---------------------------------------------

In the root of the cloned repository, you will find a file named *testsCatalog.yaml*, in which you have to specify the tests you want to run. To run a certain test simply set its *run* variable to the True Boolean value.
On the other hand, if you don't want it to be run set this value to False. Please find below, a description of each test that has already been integrated in the Test-Suite:

Deep Learning using GPUs
=============================

(This test is currently under development and will be available in future releases)

The 3DGAN application is a prototype developed to investigate the possibility to use a Deep Learning approach to speed-up the simulation of particle physics detectors. The benchmark measures the total time needed to train a
3D convolutional Generative Adversarial Network (GAN) using a data-parallel approach on distributed systems.
It is based on MPI for communication. As such, it tests the performance of single nodes (GPUs cards) but also latency and bandwidth of nodes interconnects and data access. The training uses a Kubernetes cluster (GPU flavored) with Kubeflow and MPI.

If selected, the suite will provision a Kubernetes cluster -GPU flavored- specifically for this test.
For this test, apart from the *run* variable, the following can be set in the *testsCatalog.yaml* file:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - nodes
     - Number of nodes to be used for the deployment. Default: max number of nodes available.
   * - flavor
     - Terraform definition of the flavor to be used for this test's cluster. (required)


- Contributors/Owners: Sofia Vallecorsa (CERN) - sofia.vallecorsa AT cern.ch; Jean-Roch Vlimant (Caltech)
- |Repository_mpi|

.. |Repository_mpi| raw:: html

  <a href="https://github.com/svalleco/mpi_learn" target="_blank">Repository</a>


S3 endpoint tests
=====================
A simple S3 test script to test functionality of S3-like endpoints, checking the following:
S3 authentication (access key + secret key), PUT, GET, GET with prefix matching, GET chunk and GET multiple chunks.

For this test, apart from the *run* variable, the following ones must be set on the *testsCatalog.yaml* file:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - endpoint
     - Endpoint under which your S3 bucket is reachable. This URL must not include the bucket name but only the host.
   * - accessKey
     - Access key for S3 resource management.
   * - secretKey
     - Secret key for S3 resource management.

Note that the provider has to allow using S3 clients such as s3cmd or aws-cli.
For example, specifically for GCP, interoperability has to be enabled.

- Contributors/Owners: Oliver Keeble (CERN) - oliver.keeble AT cern.ch
- |Repository_s3|

.. |Repository_s3| raw:: html

  <a href="https://gitlab.cern.ch/okeeble/s3test" target="_blank">Repository</a>


Data Export: From the commercial cloud provider to Zenodo
===============================================================
When using cloud credits, when the credit is exhausted, data can be repatriated or moved to a long-term data storage service. The example used in this test uses
|Zenodo_link| service maintained by CERN, verifying that the output data can be taken from the cloud provider to Zenodo.

- Contributors/Owners: Ignacio Peluaga (CERN) - ignacio.peluaga.lozada AT cern.ch
- |Repository_ce|

.. |Repository_ce| raw:: html

  <a href="https://github.com/ignpelloz/cloud-exporter" target="_blank">Repository</a>

.. |Zenodo_link| raw:: html

  <a href="https://zenodo.org/" target="_blank">Zenodo</a>


Containerised CPU Benchmarking
==========================================
Suite containing several CPU benchmarks used for High Energy Physics (HEP).
The following benchmarks are run on the cloud provider, using a containerised approach:

* DIRAC Benchmark
* ATLAS Kit Validation
* Whetstone: from the UnixBench benchmark suite.
* Hyper-benchmark: A pre-defined sequence of measurements and fast benchmarks.

- Contributors/Owners: Domenico Giordano (CERN) - domenico.giordano AT cern.ch
- |Repository_cpu|

.. |Repository_cpu| raw:: html

  <a href="https://gitlab.cern.ch/cloud-infrastructure/cloud-benchmark-suite" target="_blank">Repository</a>


Networking performance measurements
==========================================
perfSONAR is a network measurement toolkit designed to provide federated coverage of paths, and help to establish end-to-end usage expectations.

In this test, a perfSONAR testpoint is created using a containerised approach on the cloud provider infrastructure.
The following tests are launched end to end:

- throughput: A test to measure the observed speed of a data transfer and associated statistics between two endpoints.
- rtt: Measure the round trip time and related statistics between hosts.
- trace: Trace the path between IP hosts.
- latencybg: Continuously measure one-way latency and associated statistics between hosts and report back results periodically.

The endpoint for these tests must be specified at testsCatalog.yaml's *perfsonarTest.endpoint* variable.
Note if the server on the provided endpoint does not allow or support a subset of these tests, those will fail but the others would still be carried out.
Use endpoints from:

* |link1|
* |link2|
* |link3|

.. |link1| raw:: html

  <a href="https://fasterdata.es.net/performance-testing/perfsonar/esnet-perfsonar-services/esnet-iperf-hosts/" target="_blank">List of throughput hosts</a>

.. |link2| raw:: html

  <a href="http://perfsonar-otc.hnsc.otc-service.com/toolkit/" target="_blank">perfSONAR Toolkit</a>

.. |link3| raw:: html

  <a href="http://stats.es.net/ServicesDirectory/" target="_blank">Lookup Services Directory</a>

- Contributors/Owners: Shawn Mckee (University of Michigan) - smckee AT umich.edu; Marian Babik CERN) - marian.babik AT cern.ch
- |Repository_perf|

.. |Repository_perf| raw:: html

  <a href="https://github.com/perfsonar/perfsonar-testpoint-docker" target="_blank">Repository</a>


FDMNES: Simulation of X-ray spectroscopies
=================================================

(This test is currently under development and will be available in future releases)

The FDMNES project provides the research the community a user friendly code to simulate x-ray spectroscopies, linked to the real absorption (XANES, XMCD) or resonant scattering (RXD in bulk or SRXRD for surfaces) of synchrotron radiation.
It uses parallel calculations using OpenMPI. As an HPC test FDMNES is rather heavy on CPU and Memory and light on I/O.
The objective of this test is to understand which configuration of FDMNES is the most efficient and which type of tasks and calculations can be done in a give cloud provider.

If selected, the suite will provision a Kubernetes cluster -HPC flavored- specifically for this test.
For this test, apart from the *run* variable, the following can be set in the *testsCatalog.yaml* file:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - nodes
     - Number of nodes to be used for the deployment.
   * - flavor
     - Terraform definition of the flavor to be used for this test's cluster. (required)

- Contributors/Owners: Rainer Wilcke (ESRF) - wilcke AT esrf.fr
- |Repository_fdmnes|

.. |Repository_fdmnes| raw:: html

  <a href="http://neel.cnrs.fr/spip.php?article3137&lang=en" target="_blank">Repository</a>


DODAS: Dynamic On Demand Analysis Services test
====================================================

DODAS is a system designed to provide a high level of automation in terms of provisioning, creating, managing and accessing a pool of heterogeneous computing
and storage resources, by generating clusters on demand for the execution of HTCondor workload management system. DODAS allows to seamlessly join the
HTCondor Global Pool of CMS to enable the dynamic extension of existing computing resources. A benefit of such an architecture is that it provides high
scaling capabilities and self-healing support that results in a drastic reduction of time and cost, through setup and operational efficiency increases.

If one wants to deploy this test, the machines in the general cluster (to which such test is deployed), should have rather big disks as the image for this test is 16GB.
To set the disk size use the storageCapacity variable from configs.yaml.

- Contributors/Owners: Daniele Spiga (INFN) - daniele.spiga@pg.infn.it ; Diego Ciangottini (INFN) - diego.ciangottini@cern.ch
- |Repository_dodas|

.. |Repository_dodas| raw:: html

  <a href="https://dodas-ts.github.io/dodas-doc/" target="_blank">Repository</a>
