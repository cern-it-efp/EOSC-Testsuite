CloudStack
---------------------------------------------

Variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - It's value must be "cloudstack". (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - flavor
     - Flavor to be used for the main cluster. (required)
   * - openUser
     - User to be used for ssh connections. Root user will be used by default.
   * - keyPair
     - Name of the key to be used. Has to be created or imported beforehand. (required)
   * - securityGroups
     - Security groups array.
   * - zone
     - The zone in which to create the compute instances. (required)
   * - template
     - OS Image to be used for the VMs. (required)
   * - storageCapacity
     - VM's disk size.
   * - authFile
     - Path to the file containing the CloudStack credentials. See below the structure of such file. (required)

CloudStack credentials file's structure:

.. code-block:: console

  [cloudstack]
  url = your_api_url
  apikey = your_api_key
  secretkey = your_secret_key
