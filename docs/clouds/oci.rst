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

Oracle Cloud Infrastructure credentials file's must be a YAML file containing only the following variables:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - auth_private_key_path
     - Path to the private key to be used to authenticate to OCI. This is not the key to be used to ssh into the machines.
   * - user_ocid
     - User's OCID.
   * - tenancy_ocid
     - Tenancy's OCID.
   * - fingerprint
     - Authentication key's fingerprint.
   * - region
     - Region to be used.

It is also possible to use OKE to provision the cluster, for this refer to section :ref:`Using existing clusters<using-existing-clusters>`.
