CloudStack
---------------------------------------------

CloudStack specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - keyPair
     - Name of the key to be used. Has to be created or imported beforehand. (required)
   * - zone
     - The zone in which to create the compute instances. (required)
   * - template
     - OS Image to be used for the VMs. (required)
   * - authFile
     - Path to the file containing the CloudStack credentials. See below the structure of such file. (required)
   * - securityGroups
     - Security groups array.
   * - storageCapacity
     - VM's disk size.

CloudStack credentials file's structure:

.. code-block:: console

  [cloudstack]
  url = your_api_url
  apikey = your_api_key
  secretkey = your_secret_key
