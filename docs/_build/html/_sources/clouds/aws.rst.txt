AWS
---------------------------------------------
It is also possible to use EKS to provision the cluster, for this refer to section "Using existing clusters".

**AWS' specific variables for configs.yaml:**

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - It's value must be "aws". (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - flavor
     - Flavor to be used for the main cluster. (required)
   * - openUser
     - User to be used for ssh connections. (required)
   * - region
     - The region in which to create the compute instances. (required)
   * - sharedCredentialsFile
     - The authentication method supported is AWS shared credential file. Specify here the absolute path to such file. (required)
   * - ami
     - AMI for the instances. (required)
   * - keyName
     - Name of the key for the instances. (required)
