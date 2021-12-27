Orange's Flexible Engine
---------------------------------------------

Orange's Flexible Engine specific variables for configs.yaml:

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
   * - imageID
     - ID of the image to be used on the VMs. (required)
   * - openUser
     - User for initial SSH connections. (required)
   * - region
     - Region where the deployments should be performed. (required)
   * - availabilityZone
     - Availability Zone. (required)
   * - flavor
     - VM flavor. (required)
   * - bandwidth
     - VM's public bandwidth in Mbps, maximum 1000. (required)
   * - staticIPs
     - Array of Elastic IPs to use, instead of automatically allocated ones. If used, the number of nodes to be provisioned is determined by the size of this array.

Credentials file's structure:

.. code-block:: console

  accessKey: 123456789abcd # access key
  secretKey: 123456789abcd # security key
