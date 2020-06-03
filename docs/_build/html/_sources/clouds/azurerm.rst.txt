Azure
---------------------------------------------

It is also possible to use AKS to provision the cluster, for this refer to section "Using existing clusters".

Install az CLI and configure credentials with 'az login'.
Note resource group, security group, and subnet have to be created in advance.

Variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - It's value must be "azurerm". (required)
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
   * - securityGroupID
     - The ID of the Network Security Group to associate with the VMs's network interfaces (required)
   * - subnetId
     - Reference to a subnet in which the NIC for the VM has been created. (required)
   * - image.publisher
     - Specifies the publisher of the image used to create the virtual machines. (required)
   * - image.offer
     - Specifies the offer of the image used to create the virtual machines. (required)
   * - image.sku
     - Specifies the SKU of the image used to create the virtual machines. (required)
   * - image.version
     - Specifies the version of the image used to create the virtual machines. (required)


Note: the security group and subnet -virtual network too- have to be created beforehand and their ID's used at configs.yaml.
Also, if image's *publisher*, *offer*, *sku* and *version* are omitted, the following defaults will be used:

- publisher = OpenLogic

- offer = CentOS

- sku = 7.5

- version = latest
