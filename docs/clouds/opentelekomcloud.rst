T-Systems' Open Telekom Cloud
---------------------------------------------

To allow the VMs access the internet, Shared SNAT has to be enabled on the default VPC, which will be used for the suite run.

OTC specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - It's value must be "opentelekomcloud". (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - flavor
     - Flavor to be used for the main cluster. (required)
   * - keyPair
     - Name of the key to be used. Has to be created or imported beforehand. (required)
   * - securityGroups
     - Security groups array.
   * - storageCapacity
     - VM's disk size. The VMs will boot from disk, this sets the size of it. (required)
   * - authFile
     - Path to the yaml file containing the OTC credentials. See below the structure of such file. (required)
   * - imageID
     - ID of the image to be used on the VMs. (required)
   * - openUser
     - User to be used for ssh connections. (required)
   * - domainName
     - OTC Domain Name. (required)
   * - tenantName
     - OTC Tenant Name. (required)

Open Telekom Cloud credentials file's structure:

.. code-block:: console

  accK: 123456789abcd
  secK: 123456789abcd
