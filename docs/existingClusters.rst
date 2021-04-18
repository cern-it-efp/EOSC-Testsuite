.. _using-existing-clusters:

4. Using existing clusters
---------------------------------------------

It's possible to use this tool for testing providers that support Kubernetes as a Service. This means the provider offers the user a way for simply creating a cluster.
In case one wants to validate a provider that offers this and want to take advantage of it, skip the Terraform steps and when running the test-suite, use option *--onlyTest*.

Note that the kubeconfig files have to be placed in the following locations, according to whether the test was selected or not:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Test / Cluster
     - Path to kubeconfig
   * - Shared cluster
     - EOSC-Testsuite/src/tests/shared/config
   * - dlTest cluster
     - EOSC-Testsuite/src/tests/dlTest/config
   * - hpcTest cluster
     - EOSC-Testsuite/src/tests/hpcTest/config
   * - proGANTest cluster
     - EOSC-Testsuite/src/tests/proGANTest/config
