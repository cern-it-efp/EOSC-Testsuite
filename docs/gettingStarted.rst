1. Getting started
---------------------------------------------
This section guides the user on the whole process of preparation for running the suite, from installation of dependencies to configuration of the tool.

To ease this process, we do recommend using a Docker image that we provide which already contains the dependencies below described (Terraform, Ansible, kubectl, etc).
Refer to section :ref:`Using Docker<using-docker>` to use the Docker image we provide to avoid dealing with required packages and dependencies.

1.1 Dependencies
==========================
This test-suite requires some packages, please see below.

Terraform
^^^^^^^^^^^^^^^^
Terraform is the tool that creates the VMs that will later conform a Kubernetes cluster. Download and install |Terraform_link| on your machine.

.. |Terraform_link| raw:: html

  <a href="https://learn.hashicorp.com/terraform/getting-started/install.html" target="_blank">Terraform</a>

Ansible
^^^^^^^^^^^^^^^^
Ansible is used to configure the VMs and install packages on them in order to bootstrap the cluster. Follow the steps |Ansible_link| to install it.

.. |Ansible_link| raw:: html

  <a href="https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-with-pip" target="_blank">here</a>

Kubernetes client
^^^^^^^^^^^^^^^^^^^^^
In order to manage the Kubernetes cluster remotely, install |kubectl_link| on your machine.

.. |kubectl_link| raw:: html

  <a href="https://kubernetes.io/docs/tasks/tools/install-kubectl/" target="_blank">kubectl</a>

Python
^^^^^^^^^
Python version 3 is required.
The following python packages are required, install them with pip3:

- pyyaml

- jsonschema

- kubernetes

- requests


1.2 SSH key
==================
A ssh key pair is needed to establish connections to the VMs to be created later. Therefore, you must create (or import) this key on your provider, when needed, beforehand.
Note errors may occur if your key does not have the right permissions. Set these to the right value using the following command:

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


1.4 Permissions
==========================================
During its run, the suite creates files and folders inside the directory *EOSC-Testsuite*: Kubernetes resource definition files, log and results files and folders, etc.
Therefore, the user running the suite must have enough permissions to accomplish such tasks.

1.5 Clone and prepare
==========================================
Cloning repository
^^^^^^^^^^^^^^^^^^^^^^^
Clone the repository as follows and cd into it. Note this step is not needed when using the provided Docker image, the repository is already cloned there.

.. code-block:: console

    $ git clone https://github.com/cern-it-efp/EOSC-Testsuite.git
    $ cd EOSC-Testsuite


Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two YAML files have to be filled to configure the run. Examples of these two files can be found inside the *examples* folder of the repository.

``testsCatalog.yaml``

This file gathers details related to the tests that should be deployed.
Refer to the section :ref:`Test Catalog<tests-catalog>` to learn how to fill this file.

``configs.yaml``

This file gathers general details required to provision the infrastructure. The file also contains a section named *costCalculation*.
Refer to the section :ref:`Cost of run calculation<cost-of-run-calculation>` to learn more about the estimated cost calculation feature and to understand how to fill that part.

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
     - Flavor to be used for the main cluster. (required)
   * - openUser
     - User to be used for ssh connections.
   * - storageCapacity
     - Storage size to have on the VM.


**Provider/cloud specific variables:**

.. toctree::
   :maxdepth: 1
   :glob:

   clouds/*

To run the suite on a provider/cloud that is not listed above (supporting Terraform or not), refer to the section :ref:`No Terraform runs <no-terraform-runs>`.


.. _using-docker:

1.6 Using Docker
===================
A Docker image has been built and pushed to Docker hub. This image allows you to skip section "Dependencies" and jump to "SSH key", you can see the Dockerfile here.

Run the container (pulls the image first):

.. code-block:: console

    $ docker run -it cernefp/tslauncher

You will get a terminal on the container, directly inside the cloned repository.
