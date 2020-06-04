GCP
---------------------------------------------

It is also possible to use GKE to provision the cluster, for this refer to section "Using existing clusters". You will have to |use_gke| too.

GCP specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - providerName
     - It's value must be "google". (required)
   * - pathToKey
     - Path to the location of your private key, to be used for ssh connections. (required)
   * - flavor
     - Flavor to be used for the main cluster. (required)
   * - openUser
     - User to be used for ssh connections. Note VM specific keys are not supported, only project-wide SSH keys are.(required)
   * - zone
     - The zone in which to create the compute instances. (required)
   * - pathToCredentials
     - Path to the GCP JSON credentials file (note this file has to be downloaded in advance from the GCP console). (required)
   * - image
     - Image for the instances. (required)
   * - project
     - Google project under which the infrastructure has to be provisioned. (required)
   * - gpuType
     - Type of GPU to be used. Needed if the Deep Learning test was selected at testsCatalog.yaml.


.. |use_gke| raw:: html

  <a href="https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials?hl=en_US&_ga=2.141757301.-616534808.1554462142" target="_blank">fetch the kubectl kubeconfig file</a>
