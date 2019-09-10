1. Getting started
---------------------------------------------
Please follow the steps below in order to deploy tests in a cloud provider:

Refer to section "Using Docker" to use the Docker image we provide to avoid dealing with required packages and dependencies.

1.1 Dependencies
==========================
This test-suite requires some packages to work properly and these must be installed by yourself directly. Please see below.

Terraform
^^^^^^^^^^^^^^^^
Terraform is the tool that creates the VMs that will later become a Kubernetes cluster. The test-suite makes use of it so download and
install |Terraform_link| on your machine.
In some cases, providers are not fully supported by Terraform, however they might provide plugins to bridge this gap. In such cases, please refer to the documentation of the provider to download the plugin.
Once downloaded, this must be placed at *~/.terraform.d/plugins* and execution permissions must be given to it (*+x*).

.. |Terraform_link| raw:: html

  <a href="https://learn.hashicorp.com/terraform/getting-started/install.html" target="_blank">Terraform</a>

Kubernetes client
^^^^^^^^^^^^^^^^^^^^^
In order to manage the Kubernetes cluster locally instead of using the master node, install |kubectl_link| on your machine.

.. |kubectl_link| raw:: html

  <a href="https://kubernetes.io/docs/tasks/tools/install-kubectl/" target="_blank">kubectl</a>

Python
^^^^^^^^^
Python version 3 is required.
The following python packages are required:

- pyyaml

- jsonschema

- kubernetes

- requests

Please install them with pip3.

1.2 SSH key
==================
A ssh key pair is needed to establish connections to the VMs to be created later. Therefore, you must create (or import) this key on your provider
beforehand and place the private key at *~/.ssh/id_rsa*.
Note errors may occur if your key doesn't have the right permissions. Set these to the right value using the following command:

.. code-block:: console

    $ chmod 600 path/to/key

1.3 Security groups
==========================================
The following ports have to be opened:

- 22/TCP (SSH)

- 6443/TCP (Kubernetes API)

- 10250/TCP	(API which allows node access)

- 8472/UDP (Flannel overlay network, k8s pods communication)

1.4 Networking and IPs
==========================================
Some providers do not allocate public IPs to the VMs but use NAT. Hence the VM can be reached from outside but that IP is not really residing on the VM. This causes
conflicts when creating the Kubernetes cluster. If one wants to run the Test-Suite on a provider of this case, then the suite must be launched from within the
network the nodes will be connected to, this is a private network. In other words, **a VM will have to be created first manually** and the Test Suite will have to be
triggered from there.

1.5 Download and preparation
==========================================
Cloning repository
^^^^^^^^^^^^^^^^^^^^^^^
Please clone the repository as follows and cd into it:

.. code-block:: console

    $ git clone https://github.com/cern-it-efp/OCRE-Testsuite.git
    $ cd OCRE-Testsuite

Configuration
^^^^^^^^^^^^^^^^^^^^^^^^
While completing this task, please refer to |Terraform_docs_link| in order to complete it successfully as some parts are
provider specific and differ from one provider to another.

.. |Terraform_docs_link| raw:: html

  <a href="https://www.terraform.io/docs/providers/" target="_blank">Terraform's documentation</a>

You will find in the root of the cloned repository a folder named *configurations*. That folder must containing the following files:

``configs.yaml (required)``

Its variables:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | Name of the provider for Terraform. (required)                                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|providerInstanceName   | Compute instance name for Terraform. This is provider specific. (required)                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | | Flavor to be used for the main cluster. This has to be specified as a key-value                                           |
|                       | | pair according to the provider. (required)                                                                                |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | | User to be used in case the provider doesn't allow root ssh. If not specified,                                            |
|                       | | root will be used for ssh connections.                                                                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+


Note that it's possible to choose between "Docker Community Edition" and "Docker Engine" (older Docker packages). However it's **highly recommended** to leave these
variables empty to create a cluster with the latest stack.

The file also contains a section named *costCalculation*. Refer to the section "Cost of run calculation" to understand how to fill that part.


``testsCatalog.yaml (required)``

Refer to the section "Test Catalog" to learn how to fill this file.

``credentials``

This file must contains .tf (HCL) code for authentication that goes on the provider definition section of a Terraform configuration file (i.e AWS)
In case this file is empty, the TS assumes an external authentication method: like env variables (i.e Openstack) or CLI (i.e Azure).
Note that if you aim to use external authentication but you need something inside the provider section of the Terraform configuration file (i.e AWS region), this file is the place to define that.

``instanceDefinition (required)``

In this file one should write all the key-pair values that would be written on the body of an instance definition resource on Terraform, according to the cloud one wants to test.
Please refer to the documentation of the cloud provider to check which pairs you need to specify. In any case, you can run the Test-Suite (next steps) and if there is any missing
pair a message will be shown in the terminal telling you which ones these are. This is how you must specify each pair::

  <YOUR_PROVIDER'S_STRING_FOR_A_KEY> = "<VALUE_GIVEN_FOR_THAT_KEY>"

An example (Exoscale cloud provider)::

  display_name = "kubenode"#NAME
  template = "Linux CentOS 7.5 64-bit"
  key_pair = "k_cl"
  security_groups = ["kgroup"]
  disk_size = 50
  zone = "ch-gva-2"

One of the properties specified on the block that defines a compute node (VM) is the flavor or machine type. This property must not be specified on instanceDefinition but on configs.yaml's flavor.

Please pay attention in this section to the name for the instance. A random string will be added later to the name given to the instance in order to avoid DNS issues when
running the test-suite several times. To achieve this, the block must contain the '#NAME' placeholder. When specifying the name for the instance, please follow this structure::

  <YOUR_PROVIDER'S_STRING_FOR_NAME> = "<NAME_FOR_YOUR_INSTANCES>"#NAME

Now, lets assume your provider's string for the instance name is "display_name", and you want to call your instances "kubenode" then you should write::

  display_name = "kubenode"#NAME

Note the '#NAME'!

| [**NOTE 1**: This will be taken as a whole block and placed directly on a .tf file]
| [**NOTE 2**: Clouds that don't support resource creation with Terraform or k8saaS can't currently be tested with this Test-Suite]


``Dependencies``

This file takes also HCL code. There are providers for which dependencies are required, for example Azure: Terraform can't create a VM if there is no NIC for it.
Then this is the file to define those dependencies needed by the VMs.


Configuration examples
^^^^^^^^^^^^^^^^^^^^^^^^^^

Examples of all configuration files for several public cloud providers can be found inside *examples*.
Find below these lines details on how to run the suite on some of the main providers:

``Azure``

(Find the example files at *examples/azure*. It is also possible to use AKS to provision the cluster, for this refer to section "Using existing clusters".)

Install az CLI and configure credentials with 'az login'.

``AWS``

(Find the example files at *examples/aws*. It is also possible to use EKS to provision the cluster, for this refer to section "Using existing clusters".)

Region, access key and secret key must be hardcoded in the file *configurations/credentials*.

``GCP``

(Example files at *examples/gcp*. It is also possible to use GKE to provision the cluster, for this refer to section "Using existing clusters".)

For authentication, donwload the JSON file with the credentials from the Google Cloud console. Then, the file *configurations/credentials* must contain *credentials = "${file("CREDENTIALS_FILE")}"* and
*project = "PROJECT_ID"*, where CREDENTIALS_FILE should be the path to the downloaded file and PROJECT_ID the id of your GCP project.

The VMs need public IP's (NAT) to connect to the internet if the network used it the "default" one and differing to other providers these are
not allocated unless specified, using network_interface.access_config{} in the instance definition.

.. |use_gke| raw:: html

  <a href="https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials?hl=en_US&_ga=2.141757301.-616534808.1554462142" target="_blank">fetch the kubectl kubeconfig file</a>


1.6 Using Docker
===================
A Docker image has been built and pushed to Docker hub. This image allows you to skip section "1.1 Dependencies" and jump to "1.2 SSH key".

Run the container (pulls the image first):

.. code-block:: console

    $ docker run --net=host -it ipeluaga/tslauncher

Note the option '--net=host'. Without it, the container wouldn't be able to connect to the nodes, as it would not be in the same network as them and it is likely the nodes will not have public IPs. With that option, the container will use the network used by its host, which will be sharing the network with the nodes.

You will get a session on the container, directly inside the cloned repository.
