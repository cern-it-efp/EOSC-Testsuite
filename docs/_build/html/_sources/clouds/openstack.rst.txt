OpenStack
---------------------------------------------

Regarding authentication, download the OpenStack RC File containing the credentials from the Horizon dashboard and source it.

OpenStack specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - storageCapacity
     - VM's disk size. The VMs will boot from disk, this sets the size of it. (required)
   * - imageID
     - OS Image ID to be used for the VMs. (required)
   * - keyPair
     - Name of the key to be used. Has to be created or imported beforehand. (required)
   * - securityGroups
     - Security groups array.
   * - region
     - The region in which to create the compute instances. If omitted, the region specified in the credentials file is used.
   * - availabilityZone
     - The availability zone in which to create the compute instances.
   * - networkName
     - Name of the newtork to be used.
