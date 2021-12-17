Oracle Cloud Infrastructure
---------------------------------------------

OCI specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - ssh_public_key_path
     - Path to the public key belonging to your private key at pathToKey. This will be injected to the VMs (required)
   * - authFile
     - Path to the yaml file containing the OTC credentials. See below the structure of such file. (required)
   * - image_ocid
     - The OCID of the image to be used on the VMs. (required)
   * - compartment_ocid
     - Compartment's OCID. (required)
   * - availability_domain
     - Availability domain to be used. (required)
   * - subnet_ocid
     - The OCID of the subnet to be used. (required)
   * - storageCapacity
     - VM's disk size.
   * - useFlexShape
     - Indicates if the selected flavor is a flexible shape (such as VM.Optimized3.Flex). If this is set to false and the used flavor is a flexible one, the instances will be created with the default configuration values for the specified shape.

When using a flexible shape, specify also the following arguments (note these would be only considered if useFlexShape is set to true):

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - ocpus
     - Specify the cores for the VMs.
   * - memoryInGbs
     - Specify the memory in GB for the VMs.

Oracle Cloud Infrastructure credentials file's must be a YAML file containing only the following variables:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - privateKeyPath
     - Path to the private key to be used to authenticate to OCI. This is not the key to be used to ssh into the machines.
   * - userOcid
     - User's OCID.
   * - tenancyOcid
     - Tenancy's OCID.
   * - fingerprint
     - Authentication key's fingerprint.
   * - region
     - Region to be used.

It is also possible to use OKE to provision the cluster, for this refer to section :ref:`Using existing clusters<using-existing-clusters>`.
