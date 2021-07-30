CloudSigma
---------------------------------------------

CloudSigma specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - storageCapacity
     - VM's disk size. The VMs will boot from disk, this sets the size of it. Measured in bytes. (required)
   * - pathToPubKey
     - Path to your public key, which is injected into the VMs. (required)
   * - authFile
     - Path to a YAML file containing the credentials. See the details below this table. (required)
   * - openUser
     - Must be set to `cloudsigma`. (required)
   * - location
     - Location where the deployments should be performed. (required)
   * - clone_drive_id
     - UUID of a library drive to clone. Can be taken from the URL when browsing drives at https://gva.cloudsigma.com/ui/4.0/library. (required)
   * - flavor.memory
     - VM's RAM measured in bytes (max is 137438953472). (required)
   * - flavor.cpu
     - VM's CPU Clock speed measured in MHz (max is 124000). (required)

Credentials file's example:

.. code-block:: console

  username: someone@email.com # UI email
  password: abcd123! # UI password
