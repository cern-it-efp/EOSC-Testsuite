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

Ansible
^^^^^^^^^^^^^^^^
Ansible is used to configure the VMs and install packages on them in order to bootstrap the cluster. Follow the steps |Ansible_link| to install it.

.. |Ansible_link| raw:: html

  <a href="https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-with-pip" target="_blank">here</a>

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

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

   * - Port
     - Protocol
     - Functionality
   * -
     - ICMP
     - Connectivity test
   * - 22
     - TCP
     - SSH
   * - 6443
     - TCP
     - Kubernetes API
   * - 10250
     - TCP
     - API which allows node access
   * - 8472
     - UDP
     - Flannel overlay network, k8s pods communication


1.4 Networking and IPs
==========================================
Some providers do not allocate public IPs to the VMs but use NAT. Hence the VM can be reached from outside but that IP is not really residing on the VM. This causes
conflicts when creating the Kubernetes cluster. If one wants to run the Test-Suite on a provider of this case, then the suite must be launched from within the
network the nodes will be connected to, this is a private network. In other words, **a VM will have to be created first manually** and the Test Suite will have to be
triggered from there.

1.5 Clone and prepare
==========================================
Cloning repository
^^^^^^^^^^^^^^^^^^^^^^^
Please clone the repository as follows and cd into it. This step is not needed when using the provided Docker image, the repository is already cloned there.

.. code-block:: console

    $ git clone https://github.com/cern-it-efp/EOSC-Testsuite.git
    $ cd EOSC-Testsuite


Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two YAML files have to be filled to configure the run. Examples of these two files can be found inside the examples folder of the repository.

``testsCatalog.yaml``

This file gathers details related to the tests that should be deployed.
Refer to the section "Test Catalog" to learn how to fill this file.

``configs.yaml``

This file gathers general details required to provision the infrastructure.
The file also contains a section named *costCalculation*. Refer to the section "Cost of run calculation" to understand how to fill that part.
The suite will create itself the Terraform files on the fly according to the configuration provided.

**General variables:**

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - Terraform name of the provider. (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - flavor
     - Flavor to be used for the main cluster.
   * - openUser
     - User to be used for ssh connections.
   * - location
     - The region in which to create the compute instances. (required)
   * - subscriptionId
     - ID of the subscription. (required)
   * - resourceGroupName
     - Specifies the name of the Resource Group in which the Virtual Machine should exist. (required)
   * - pubSSH
     - Public SSH key of the key specified at configs.yaml's pathToKey. (required)

**Provider specific variables:**

.. toctree::
   :maxdepth: 1
   :glob:

   clouds/*


1.6 Using Docker
===================
A Docker image has been built and pushed to Docker hub. This image allows you to skip section "Dependencies" and jump to "SSH key".

Run the container (pulls the image first):

.. code-block:: console

    $ docker run --net=host -it cernefp/tslauncher

Note the option '--net=host'. Without it, the container wouldn't be able to connect to the nodes, as it would not be in the same network as them and it is likely the nodes will not have public IPs. With that option, the container will use the network used by its host, which will be sharing the network with the nodes.

You will get a session on the container, directly inside the cloned repository.
