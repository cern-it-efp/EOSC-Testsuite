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

+------+----------+----------------------------------------------------+
|Port  | Protocol |Functionality                                       |
+======+==========+====================================================+
| -    | ICMP     |Connectivity test                                   |
+------+----------+----------------------------------------------------+
|22    | TCP      |SSH                                                 |
+------+----------+----------------------------------------------------+
|6443  | TCP      |Kubernetes API                                      |
+------+----------+----------------------------------------------------+
|10250 | TCP      |API which allows node access                        |
+------+----------+----------------------------------------------------+
|8472  | UDP      |Flannel overlay network, k8s pods communication     |
+------+----------+----------------------------------------------------+

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

    $ git clone https://github.com/cern-it-efp/EOSC-Testsuite.git
    $ cd EOSC-Testsuite

Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

While completing this task, please refer to |Terraform_docs_link| in order to complete it successfully as some parts are
provider specific and differ from one provider to another.

.. |Terraform_docs_link| raw:: html

  <a href="https://www.terraform.io/docs/providers/" target="_blank">Terraform's documentation</a>


You will find in the root of the cloned repository a folder named *configurations*. That folder must containing the following files:


``testsCatalog.yaml (required)``

  Refer to the section "Test Catalog" to learn how to fill this file.


``configs.yaml (required)``

| [**NOTE**: For running on Azure, AWS, GCP, OpenStack, CloudStack and Exoscale refer to the section "Main clouds" below. In those cases, only configs.yaml and testsCatalog.yaml are needed.]

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


``credentials``

This file must contains .tf (HCL) code for authentication that goes on the provider definition section of a Terraform configuration file (i.e AWS)
In case this file is empty, the TS assumes an external authentication method: like env variables (i.e OpenStack) or CLI (i.e Azure).
Note that if you aim to use external authentication but you need something inside the provider section of the Terraform configuration file (i.e AWS region), this file is the place to define that.

``instanceDefinition (required)``

In this file one should write all the key-pair values that would be written on the body of an instance definition resource on Terraform, according to the cloud one wants to test.
Please refer to the documentation of the cloud provider to check which pairs you need to specify. In any case, you can run the Test-Suite (next steps) and if there is any missing
pair a message will be shown in the terminal telling you which ones these are. This is how you must specify each pair::

  <YOUR_PROVIDER'S_STRING_FOR_A_KEY> = "<VALUE_GIVEN_FOR_THAT_KEY>"

An example::

  display_name = "NAME_PH"
  template = "Linux CentOS 7.5 64-bit"
  key_pair = "k_cl"
  security_groups = ["kgroup"]
  disk_size = 50
  zone = "ch-gva-2"

One of the properties specified on the block that defines a compute node (VM) is the flavor or machine type. This property must not be specified on instanceDefinition but on configs.yaml's flavor.

Please pay attention in this section to the name for the instance, which will be set by the Test-Suite containing:

- The string "kubenode"
- A string indicating the purpose of the cluster to which the VM belongs
- A random, 4 character string to avoid DNS issues
- An integer. 0 would be the master node, 1+ would be the slaves

To achieve this, your instance definition must contain the 'NAME_PH' placeholder. When specifying the name for the instance, please follow this structure::

  <YOUR_PROVIDER'S_STRING_FOR_NAME> = "NAME_PH"

Now, let's assume your provider's string for the instance name is "display_name", then you should write::

  display_name = "NAME_PH"

As an example let's assume the suite comes up with the name "kubenode-hpcTest-aws-0", Then it would switch that name with the NAME_PH placeholder::

  display_name = "kubenode-hpcTest-aws-0"

| [**NOTE 1**: This will be taken as a whole block and placed directly on a .tf file]
| [**NOTE 2**: Clouds that don't support resource creation with Terraform or k8saaS can't currently be tested with this Test-Suite]


``Dependencies``

This file takes also HCL code. There are providers for which dependencies are required, for example Azure: Terraform can't create a VM if there is no NIC for it.
Then this is the file to define those dependencies needed by the VMs.


Main clouds: additional support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Writing Terraform files is not needed when running the suite on Azure, AWS, GCP, OpenStack, CloudStack and Exoscale.
In those cases the suite will create itself the Terraform files on the fly according to the configuration provided.
Find below these lines details on how to run the suite on these providers:

``Azure``

(Find the example files at *examples/azure*. It is also possible to use AKS to provision the cluster, for this refer to section "Using existing clusters".)

Install az CLI and configure credentials with 'az login'.

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "azurerm". (required)                                                                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster.                                                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | User to be used for ssh connections.                                                                                        |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|location               | The region in which to create the compute instances. (required)                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|subscriptionId         | ID of the subscription. (required)                                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|resourceGroupName      | Specifies the name of the Resource Group in which the Virtual Machine should exist. (required)                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pubSSH                 | Public SSH key of the key specified at configs.yaml's pathToKey. (required)                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|securityGroupID        | The ID of the Network Security Group to associate with the VMs's network interfaces (required)                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|subnetId               | Reference to a subnet in which the NIC for the VM has been created. (required)                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|image.publisher        | Specifies the publisher of the image used to create the virtual machines. (required)                                        |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|image.offer            | Specifies the offer of the image used to create the virtual machines. (required)                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|image.sku              | Specifies the SKU of the image used to create the virtual machines. (required)                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|image.version          | Specifies the version of the image used to create the virtual machines. (required)                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+

Note: the security group and subnet -virtual network too- have to be created beforehand and their ID's used at configs.yaml.
Also, if image's *publisher*, *offer*, *sku* and *version* are omitted, the following defaults will be used:

- publisher = OpenLogic

- offer = CentOS

- sku = 7.5

- version = latest

``AWS``

(Find the example files at *examples/aws*. It is also possible to use EKS to provision the cluster, for this refer to section "Using existing clusters".)

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "aws". (required)                                                                                        |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster. (required)                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | User to be used for ssh connections. (required)                                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|region                 | The region in which to create the compute instances. (required)                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|sharedCredentialsFile  | The authentication method supported is AWS shared credential file. Specify here the absolute path to such file. (required)  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|ami                    | AMI for the instances. (required)                                                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|keyName                | Name of the key for the instances. (required)                                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+


``GCP``

(Example files at *examples/gcp*. It is also possible to use GKE to provision the cluster, for this refer to section "Using existing clusters". You will have to |use_gke| too.)

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "google". (required)                                                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster. (required)                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | User to be used for ssh connections. (required)                                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|zone                   | The zone in which to create the compute instances. (required)                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToCredentials      | Path to the GCP JSON credentials file (note this file has to be downloaded in advance from the GCP console). (required)     |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|image                  | Image for the instances. (required)                                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|project                | Google project under which the infrastructure has to be provisioned. (required)                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|gpuType                | Type of GPU to be used. Needed if the Deep Learning test was selected at testsCatalog.yaml.                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+

.. |use_gke| raw:: html

  <a href="https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials?hl=en_US&_ga=2.141757301.-616534808.1554462142" target="_blank">fetch the kubectl kubeconfig file</a>

``OpenStack``

Regarding authentication, download the OpenStack RC File containing the credentials from the Horizon dashboard and source it.

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "openstack". (required)                                                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster. (required)                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | User to be used for ssh connections. Root user will be used by default.                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|imageName              | OS Image to be used for the VMs. (required)                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|keyPair                | Name of the key to be used. Has to be created or imported beforehand. (required)                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|securityGroups         | Security groups array. Must be a String, example: "[\"default\",\"allow_ping_ssh_rdp\"]"                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|region                 | The region in which to create the compute instances. If omitted, the region specified in the credentials file is used.      |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|availabilityZone       | The availability zone in which to create the compute instances.                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+


``CloudStack``

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "cloudstack". (required)                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster. (required)                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | User to be used for ssh connections. Root user will be used by default.                                                     |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|keyPair                | Name of the key to be used. Has to be created or imported beforehand. (required)                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|securityGroups         | Security groups array. Must be a String, example: "[\"default\",\"allow_ping_ssh_rdp\"]"                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|zone                   | The zone in which to create the compute instances. (required)                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|template               | OS Image to be used for the VMs. (required)                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|diskSize               | VM's disk size.                                                                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|authFile             | Path to the file containing the CloudStack credentials. See below the structure of such file. (required)                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+

CloudStack credentials file's structure:

.. code-block:: console

  [cloudstack]
  url = your_api_url
  apikey = your_api_key
  secretkey = your_secret_key


``Exoscale``

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "exoscale". (required)                                                                                   |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster. (required)                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|keyPair                | Name of the key to be used. Has to be created or imported beforehand. (required)                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|securityGroups         | Security groups array. Must be a String, example: "[\"default\",\"allow_ping_ssh_rdp\"]"                                    |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|zone                   | The zone in which to create the compute instances. (required)                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|template               | OS Image to be used for the VMs. (required)                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|diskSize               | VM's disk size. (required)                                                                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|authFile             | Path to the file containing the Exoscale credentials. See below the structure of such file. (required)                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+

Exoscale credentials file's structure:

.. code-block:: console

  [exoscale]
  key = EXOe3ca3e7621b7cd7a20f7e0de
  secret = 2_JvzFcZQL_Rg1nZSRNVheYQh9oYlL5aX3zX-eILiL4


``T-Systems' Open Telekom Cloud``

Note that to allow the VMs access the internet, Shared SNAT has to be enabled on the default VPC.

Variables for configs.yaml:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|Name                   | Explanation / Values                                                                                                        |
+=======================+=============================================================================================================================+
|providerName           | It's value must be "opentelekomcloud". (required)                                                                                   |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key (required)                                                                         |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|flavor                 | Flavor to be used for the main cluster. (required)                                                                          |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.                                                               |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.                                                              |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|keyPair                | Name of the key to be used. Has to be created or imported beforehand. (required)                                            |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|securityGroups         | Security groups array.                                                                                                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|diskSize               | VM's disk size. (required)                                                                                                  |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|authFile               | Path to the yaml file containing the OTC credentials. See below the structure of such file. (required)                      |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|imageID                | ID of the image to be used on the VMs. (required)                                                                           |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|openUser               | User to be used for ssh connections. (required)                                                                             |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|domainName             | OTC Domain Name. (required)                                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
|tenantName             | OTC Tenant Name. (required)                                                                                                 |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+

Open Telekom Cloud credentials file's structure:

.. code-block:: console

accK: 123456789abcd
secK: 123456789abcd



1.6 Using Docker
===================
A Docker image has been built and pushed to Docker hub. This image allows you to skip section "1.1 Dependencies" and jump to "1.2 SSH key".

Run the container (pulls the image first):

.. code-block:: console

    $ docker run --net=host -it cernefp/tslauncher

Note the option '--net=host'. Without it, the container wouldn't be able to connect to the nodes, as it would not be in the same network as them and it is likely the nodes will not have public IPs. With that option, the container will use the network used by its host, which will be sharing the network with the nodes.

You will get a session on the container, directly inside the cloned repository.
