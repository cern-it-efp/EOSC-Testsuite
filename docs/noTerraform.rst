.. _no-terraform-runs:

5. No Terraform runs
---------------------------------------------

It's possible to use this tool for testing providers that do not support Terraform.
In these cases, the suite will skip the Terraform provision phase and would just bootstrap the cluster and deploy the tests.
Therefore the VMs have to be provisioned beforehand and their IPs written down at configs.yaml.

The configs.yaml file for these type of run takes the following variables:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - Name of the provider being tested. (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - openUser
     - User to be used for ssh connections. (required)
   * - clusters.shared
     - IPs of the shared cluster's VMs. (Required if at least one of the general tests was selected)
   * - clusters.hpcTest
     - IPs of the HPC cluster's VMs. (Required if the HPC test was selected)
   * - clusters.dlTest
     - IPs of the GPU cluster's VMs. (Required if the GPU test was selected)

For making use of this feature use the option '--noTerraform' when running the suite.
