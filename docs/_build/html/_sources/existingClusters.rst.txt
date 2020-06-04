4. Using existing clusters
---------------------------------------------

It's possible to use this tool for testing providers that support Kubernetes as a Service. This means the provider offers the user a way for simply creating a cluster.
In case one wants to validate a provider that offers this and want to take advantage of it, simply skip steps 1.1 and 1.2 (install Terraform and manage ssh keys) and when running the test-suite, use option *--only-test*.

Note that the kubeconfig files have to be placed in the following locations, in case that test was selected:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Test / Cluster
     - Path to kubeconfig
   * - Shared cluster
     - EOSC-Testsuite/src/tests/shared/config
   * - GPU cluster
     - EOSC-Testsuite/src/tests/dlTest/config
   * - HPC cluster
     - EOSC-Testsuite/src/tests/hpcTest/config
