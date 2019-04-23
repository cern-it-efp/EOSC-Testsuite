1. Getting started
---------------------------------------------

Please follow the steps below in order to deploy tests in a cloud provider:

1.1 Install Terraform
==========================
Terraform is the tool that creates the VMs that will later become a Kubernetes cluster. The test-suite makes use of it so download and
install |Terraform_link| on your machine.
In some cases, providers are not fully supported by Terraform, however they might provide plugins to bridge this gap. In such cases, please refer to the documentation of the provider to download the plugin.
Once downloaded, this must be placed at *~/.terraform.d/plugins* and execution permissions must be given to it (*+x*).

.. |Terraform_link| raw:: html

  <a href="https://learn.hashicorp.com/terraform/getting-started/install.html" target="_blank">Terraform</a>

1.2 Manage ssh keys
==========================
A ssh key pair is needed to establish connections to the VMs to be created later. Therefore, you must create (or import) this key on your provider
beforehand and place the private key at *~/.ssh/id_rsa*. Note errors may occur if your key doesn't have the right permissions. Set these to the right value using the following command:

.. code-block:: console

    $ chmod 600 path/to/key

1.3 Dependencies
==========================
This test-suite requires some packages to work properly and these must be installed by yourself directly. Please see below.

Kubernetes client
^^^^^^^^^^^^^^^^^^^^^
In order to manage the Kubernetes cluster locally instead of using the master node, install |kubectl_link| on your machine.

.. |kubectl_link| raw:: html

  <a href="https://kubernetes.io/docs/tasks/tools/install-kubectl/" target="_blank">kubectl</a>

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
While completing this task, please refer to |Terraform_docs_link| in order to complete it successfully as some parts are
provider specific and differ from one provider to another.
You will find in the root of the cloned repository a file named *configs_raw.yaml*. You must rename it *configs.yaml* and fill it to match your requirements. **A filled example can be
found in */examples***. This file contains different sections:

.. |Terraform_docs_link| raw:: html

  <a href="https://www.terraform.io/docs/providers/" target="_blank">Terraform's documentation</a>

``general``

For specifying general variables:

+-----------------------+-----------------------------------------------------------------------+
|Name                   | Explanation / Values                                                  |
+=======================+=======================================================================+
|clusterNodes           | Number of nodes the cluster must contain, including master node.      |
+-----------------------+-----------------------------------------------------------------------+
|providerName           | Name of the provider for Terraform.                                   |
+-----------------------+-----------------------------------------------------------------------+
|providerInstanceName   | Compute instance name for Terraform. This is provider specific.       |
+-----------------------+-----------------------------------------------------------------------+
|pathToKey              | Path to the location of your private key                              |
+-----------------------+-----------------------------------------------------------------------+
|dockerCE               | Version of docker-ce to be installed. Leave empty for latest.         |
+-----------------------+-----------------------------------------------------------------------+
|dockerEngine           | Version of docker-engine to be installed. Leave empty for latest.     |
+-----------------------+-----------------------------------------------------------------------+
|kubernetes             | Version of Kubernetes to be installed. Leave empty for latest.        |
+-----------------------+-----------------------------------------------------------------------+

Note that it's possible to choose between "Docker Community Edition" and "Docker Engine" (older Docker packages). However it's **highly recommended** to leave these variables empty to create a cluster with the latest stack.

``auth``

For specifying the credentials to connect to the provider and deploy resources.

+-------------+----------------------------------------------------------------------------------------------+
|Name         | Accepted Values                                                                              |
+=============+==============================================================================================+
|useFile      | Indicate if a credentials file is used instead of secret-key pair (Boolean). Required.       |
+-------------+----------------------------------------------------------------------------------------------+
|credentials  | | String block with the required credentials.                                                |
|             | | This is not yaml but string, therefore use '=' and ' " '. (cloud provider specific).       |
+-------------+----------------------------------------------------------------------------------------------+

``instanceDefinition``

In this section one should write all the key-pair values that would be written on the body of an instance declaration resource on Terraform, according to the cloud one wants to test.
Please refer to the documentation of the cloud provider to check which pairs you need to specify. In any case, you can run the Test-Suite (next steps) and if there is any missing pair a message will be shown in the terminal telling you which ones are these. This is how you must specify each pair::

  <YOUR_PROVIDER'S_STRING_FOR_A_KEY> = "<VALUE_GIVEN_FOR_THAT_KEY>"

An example (Exoscale cloud provider)::

  display_name = "kubenode"#NAME
  template = "Linux CentOS 7.5 64-bit"
  size = "Medium"
  key_pair = "k_cl"
  security_groups = ["kgroup"]
  disk_size = 50
  zone = "ch-gva-2"

Please pay attention in this section to the name for the instance. A random string will be added later to the name given to the instance in order to avoid DNS issues when
running the test-suite several times. To achieve this, the block must contain the '#NAME' placeholder. When specifying the name for the instance, please follow this structure::

  <YOUR_PROVIDER'S_STRING_FOR_NAME> = "<NAME_FOR_YOUR_INSTANCES>"#NAME

Now, lets image you provider's string for the instance name is "display_name", and you want to call your instances "kubenode" then you should write::

  display_name = "kubenode"#NAME

Note the '#NAME'!

| [**NOTE 1**: Even though this is a yaml file, '=' is used on this section instead of ':' as that's required by Terraform files and this will be taken as a whole block and placed directly on a .tf file]
| [**NOTE 2**: Clouds that don't support resource creation with Terraform or k8saaS can't currently be tested with this Test-Suite]
