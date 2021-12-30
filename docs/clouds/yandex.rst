Yandex Cloud
---------------------------------------------

Yandex Cloud specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - storageCapacity
     - VM's disk size. The VMs will boot from disk, this sets the size of it. Measured in GB. (required)
   * - pathToPubKey
     - Path to your public key, which is injected into the VMs. (required)
   * - serviceAccountKeyFile
     - Path to a JSON file containing the credentials. (required)
   * - openUser
     - Default user for SSH connections. (required)
   * - cloudID.
     - Cloud ID. (required)
   * - folderID
     - Folder ID (required)
   * - platformID
     - Platform ID. (required)
   * - zone
     - Zone where the deployments should be performed. (required)
   * - imageID
     - OS image ID. (required)
   * - flavor.cores
     - VM number of cores. (required)
   * - flavor.memory
     - The amount of memory for the server in GB. (required)
   * - staticIPs
     - Array of Static IPs to use, instead of automatically obtained ones.
