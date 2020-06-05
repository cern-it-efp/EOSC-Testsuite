Azure
---------------------------------------------

Install az CLI and configure credentials with 'az login'.
Note resource group, security group, and subnet have to be created in advance.

Azure specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - location
     - The region in which to create the compute instances. (required)
   * - subscriptionId
     - ID of the subscription. (required)
   * - resourceGroupName
     - Specifies the name of the Resource Group in which the Virtual Machine should exist. (required)
   * - pubSSH
     - Public SSH key of the key specified at configs.yaml's pathToKey. (required)
   * - securityGroupID
     - The ID of the Network Security Group to associate with the VMs's network interfaces (required)
   * - subnetId
     - Reference to a subnet in which the NIC for the VM has been created. (required)
   * - image.publisher
     - Specifies the publisher of the image used to create the virtual machines.
   * - image.offer
     - Specifies the offer of the image used to create the virtual machines.
   * - image.sku
     - Specifies the SKU of the image used to create the virtual machines.
   * - image.version
     - Specifies the version of the image used to create the virtual machines.

The image section is optional but in case it is provided, all its 4 variables must be set.
Omitting the image section defaults to:

- publisher = OpenLogic

- offer = CentOS

- sku = 7.5

- version = latest

It is also possible to use AKS to provision the cluster, for this refer to section "Using existing clusters".
