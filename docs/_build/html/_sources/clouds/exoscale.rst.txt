Exoscale
---------------------------------------------

Variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - It's value must be "exoscale". (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - flavor
     - Flavor to be used for the main cluster. (required)
   * - keyPair
     - Name of the key to be used. Has to be created or imported beforehand. (required)
   * - securityGroups
     - Security groups array.
   * - zone
     - The zone in which to create the compute instances. (required)
   * - template
     - OS Image to be used for the VMs. (required)
   * - storageCapacity
     - VM's disk size. (required)
   * - authFile
     - Path to the file containing the Exoscale credentials. See below the structure of such file. (required)


Exoscale credentials file's structure:

.. code-block:: console

  [cloudstack]
  key = EXOe3ca3e7621b7cd7a20f7e0de
  secret = 2_JvzFcZQL_Rg1nZSRNVheYQh9oYlL5aX3zX-eILiL4
