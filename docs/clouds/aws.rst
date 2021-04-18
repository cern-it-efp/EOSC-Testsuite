AWS
---------------------------------------------

AWS specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - region
     - The region in which to create the compute instances. (required)
   * - sharedCredentialsFile
     - The authentication method supported is AWS shared credential file. Specify here the absolute path to such file. (required)
   * - ami
     - AMI for the instances. (required)
   * - keyName
     - Name of the key for the instances. (required)

It is also possible to use EKS to provision the cluster, for this refer to section :ref:`Using existing clusters<using-existing-clusters>`.
