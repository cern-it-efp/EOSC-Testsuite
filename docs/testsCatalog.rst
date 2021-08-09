.. _tests-catalog:

2. Tests Catalog
---------------------------------------------

This section describes the tests that the test suite contains.
In the root of the cloned repository, you will find a file named *testsCatalog.yaml* in which you have to specify the tests you want to run.
The test suite relies on this YAML file to deploy the tests on the clusters. To run a certain test set its *run* variable to *True*.
Please find below, a description of each test as well as additional parameters for the configuration of each.

Distributed Training of a GAN using GPUs
=============================================

The 3DGAN application is a prototype developed to investigate the possibility to use a Deep Learning approach to speed-up the simulation of particle physics detectors. The benchmark measures the total time needed to train a
3D convolutional Generative Adversarial Network (GAN) using a data-parallel approach on distributed systems.
It is based on MPI for communication. As such, it tests the performance of single nodes (GPUs cards) but also latency and bandwidth of nodes interconnects and data access. The training uses a Kubernetes cluster (GPU flavored) with Kubeflow and MPI.

If selected, the suite will provision a Kubernetes cluster -GPU flavored- specifically for this test. The test suite **assumes NVIDIA drivers are installed**. Therefore, this test can only run using an OS image that includes it.
For this test, apart from the *run* variable, the following can be set in the *testsCatalog.yaml* file:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - nodes
     - Number of nodes to be used for the deployment. Default: max number of nodes available.
   * - flavor
     - Name of the flavor to be used for this test's cluster. (required)


- Contributors/Owners: Sofia Vallecorsa (CERN) - sofia.vallecorsa AT cern.ch; Jean-Roch Vlimant (Caltech)
- |Repository_nnlo| / |Repository_mpi_learn|

.. |Repository_mpi_learn| raw:: html

  <a href="https://github.com/svalleco/mpi_learn" target="_blank">Repository MPI-learn</a>

.. |Repository_nnlo| raw:: html

  <a href="https://github.com/svalleco/NNLO" target="_blank">Repository NNLO</a>


progressive Growing of GANs using GPUs
===========================================

Single-node training, based on |progan_karras|. The |faces_dataset| is a generic dataset, used only as an example for this use case.

.. |progan_karras| raw:: html

  <a href="https://github.com/tkarras/progressive_growing_of_gans" target="_blank">Progressive Growing of GANs</a>

.. |faces_dataset| raw:: html

  <a href="" target="_blank">dataset used for this test</a>


If selected, the suite will provision a single-node Kubernetes cluster -GPU flavored- specifically for this test. The test suite **assumes NVIDIA drivers are installed**. Therefore, this test can only run using an OS image that includes it.
For this test, apart from the *run* variable, the following can be set in the *testsCatalog.yaml* file:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - flavor
     - Name of the flavor to be used for this test's cluster. (required)
   * - images_amount (1, 980)
     - Number of images to use from the data set. Minimum 1, maximum 980. (required)
   * - kimg
     - Number of images provided to the network for its training. Note 1 kimg = 1000 images. Minimum 1, maximum 12000. (required)
   * - gpus
     - Number of GPUs to use. Accepted values are 1, 2, 4 and 8. If this parameter is not used, all the available GPUs on the VM will be used.

- Contributors/Owners: Sofia Vallecorsa (CERN) - sofia.vallecorsa AT cern.ch
- |Repository_progan|

.. |Repository_progan| raw:: html

  <a href="https://github.com/svalleco/CProGAN-ME" target="_blank">Repository</a>


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


CPU Benchmarking
==========================================
Benchmarking relying on a suite containing several High Energy Physics (HEP) based benchmarks.
For this test, the VM should have at least 4 cores.
Please refer to the repository below for more details and information.

- Contributors/Owners: Domenico Giordano (CERN) - domenico.giordano AT cern.ch
- |Repository_hep_suite|

.. |Repository_hep_suite| raw:: html

  <a href="https://gitlab.cern.ch/hep-benchmarks/hep-benchmark-suite" target="_blank">Repository</a>


Networking performance measurements
==========================================
perfSONAR is a network measurement toolkit designed to provide federated coverage of paths, and help to establish end-to-end usage expectations.

In this test, a perfSONAR testpoint is created using a containerised approach on the cloud provider infrastructure.
The following tests are run between the provisioned testpoint and another perfSONAR server that the user specifies in the test's configuration (see below):

- throughput: A test to measure the observed speed of a data transfer and associated statistics between two endpoints.
- rtt: Measure the round trip time and related statistics between hosts.
- trace: Trace the path between IP hosts.
- latency: Measure one-way latency and associated statistics between hosts. Note this test does not work if the node is behind NAT.

The endpoint for these tests must be specified at testsCatalog.yaml's *perfsonarTest.endpoint* variable.
Note if the server on the provided endpoint does not allow or support any of these tests, those will fail but the others would still be carried out.
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


DODAS: Dynamic On Demand Analysis Services test
====================================================

DODAS is a system designed to provide a high level of automation in terms of provisioning, creating, managing and accessing a pool of heterogeneous computing
and storage resources, by generating clusters on demand for the execution of HTCondor workload management system. DODAS allows to seamlessly join the
HTCondor Global Pool of CMS to enable the dynamic extension of existing computing resources. A benefit of such an architecture is that it provides high
scaling capabilities and self-healing support that results in a drastic reduction of time and cost, through setup and operational efficiency increases.

If one wants to deploy this test, the machines in the general cluster (to which such test is deployed), should have rather large disks as the image for this test is 16GB.
To set the disk size use the *storageCapacity* variable from configs.yaml.

- Contributors/Owners: Daniele Spiga (INFN) - daniele.spiga@pg.infn.it ; Diego Ciangottini (INFN) - diego.ciangottini@cern.ch
- |Repository_dodas|

.. |Repository_dodas| raw:: html

  <a href="https://dodas-ts.github.io/dodas-doc/" target="_blank">Repository</a>
