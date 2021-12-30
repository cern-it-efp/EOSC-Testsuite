IBM Cloud
---------------------------------------------

IBM specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - authFile
     - Path to the yaml file containing the credentials. See below the structure of such file. (required)
   * - pathToPubKey
     - Path to your public key, which is injected into the VMs. (required)
   * - os_reference_code
     - OS image for the VMs. (required)
   * - datacenter
     - Location where the deployments should be performed. (required)
   * - flavor
     - VM flavor. (required)
   * - network_speed
     - The connection speed (in Mbps) for the instance's network components. (required)

Credentials file's example:

.. code-block:: console

  iaas_classic_username: someone@email.com #
  iaas_classic_api_key: abcd123! # Classic Infrastructure API Keys
