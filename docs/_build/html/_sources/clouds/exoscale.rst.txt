Exoscale
---------------------------------------------

Exoscale specific variables for configs.yaml:

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
   * - storageCapacity
     - VM's disk size. (required)
   * - authFile
     - Path to the file containing the Exoscale credentials. See below the structure of such file. (required)
   * - securityGroups
     - Security groups array.


Exoscale credentials file's structure:

.. code-block:: console

  [cloudstack]
  key = EXOe3ca3e7621b7cd7a20f7e0de
  secret = 2_JvzFcZQL_Rg1nZSRNVheYQh9oYlL5aX3zX-eILiL4
