Azure
---------------------------------------------

Install az CLI and configure credentials with 'az login'.
Note a resource group has to be created prior to running the test suite.

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
   * - image.publisher
     - Specifies the publisher of the image used to create the virtual machines. (required)
   * - image.offer
     - Specifies the offer of the image used to create the virtual machines. (required)
   * - image.sku
     - Specifies the SKU of the image used to create the virtual machines. (required)
   * - image.version
     - Specifies the version of the image used to create the virtual machines. (required)

For specific images (i.e. NVIDIA's), its legal terms have to be accepted:

.. code-block:: console

    $ az vm image accept-terms --urn IMAGE_URN --subscription SUBSCRIPTION_ID


It is also possible to use AKS to provision the cluster, for this refer to section :ref:`Using existing clusters<using-existing-clusters>`.
