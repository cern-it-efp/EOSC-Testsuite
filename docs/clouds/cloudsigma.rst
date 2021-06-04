CloudSigma
---------------------------------------------

CloudSigma specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - storageCapacity
     - VM's disk size. The VMs will boot from disk, this sets the size of it. (required)
   * - authFile
     - Path to the yaml file containing the credentials. See below the structure of such file. (required)

Credentials file's example:

.. code-block:: console

  username: someone@email.com
  password: abcd123!
