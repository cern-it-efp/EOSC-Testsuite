Ionos Cloud
---------------------------------------------

Ionos specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - storageCapacity
     - VM's disk size. The VMs will boot from disk, this sets the size of it. (required)
   * - authFile
     - Path to the yaml file containing the credentials. See below the structure of such file. (required)
   * - pathToPubKey
     - Path to your public key, which is injected into the VMs. (required)
   * - image_name
     - OS image for the VMs. (required)
   * - location
     - Location where the deployments should be performed. (required)
   * - flavor.cores
     - VM number of cores. (required)
   * - flavor.ram
     - The amount of memory for the server in MB. (required)

Credentials file's example:

.. code-block:: console

  username: someone@email.com # UI email
  password: abcd123! # UI password
