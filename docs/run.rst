3. Run the test-suite
------------------------------

Once the configuration steps are completed, the Test-Suite is ready to be run:

.. code-block:: console

    $ ./test_suite <options>

Options
===============
The following table describes all the available options:

+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|Name                    | Explanation / Values                                                                                                     |
+========================+==========================================================================================================================+
|--only-test             | | Run without creating the infrastructure (VMs and cluster), only deploy tests.                                          |
|                        | | Not valid for the first run.                                                                                           |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|--retry                 | | In case of errors on the first run, use this option for retrying. This will make the test-suite                        |
|                        | | try and reuse already provisioned infrastructure.                                                                      |
|                        | | Not valid for the first run, use only when VMs were provisioned but kubernetes                                         |
|                        | | bootstrapping failed.                                                                                                  |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|--no-Terraform          | | Option to avoid terraform provisionment, only ansible-playbook bootstrapping.                                          |
|                        | | To be used on providers that do not support terraform.                                                                 |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|-c, --configs           | | Specifies custom location of configs.yaml. If not used, default will be the 'configurations' folder.                   |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|-t, --testsCatalog      | | Specifies custom location of testsCatalog.yaml. If not used, default will be the 'configurations' folder.              |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|--destroy <cluster>     | | No test suite run, only destroy provisioned infrastructure.                                                            |
|                        | | Argument can be:                                                                                                       |
|                        | |   'shared': Destroy the shared cluster.                                                                                |
|                        | |   'dlTest': Destroy the GPU cluster.                                                                                   |
|                        | |   'hpcTest': Destroy the HPC cluster.                                                                                  |
|                        | |   'all': Destroy all clusters.                                                                                         |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+
|--destroy-on-completion <cluster> | | Destroy infrastructure once the test suite completes its run. Same arguments as for '--destroy' apply.        |
|                        | |                                                                                                                        |
+------------------------+--------------------------------------------------------------------------------------------------------------------------+


Other commands
==================

Once the test suite is running, you can view the provisionment logs by doing:

.. code-block:: console

    $ tail -f logs

Once the provisioning has completed and tests are deployed, you can see the pods statuses by doing:

.. code-block:: console

    $ watch kubectl get pods

If GPU and HPC tests were deployed, see their pods by doing:

.. code-block:: console

    $ watch kubectl --kubeconfig src/tests/dlTest/config get pods # For GPU cluster
    $ watch kubectl --kubeconfig src/tests/hpcTest/config get pods # For HPC cluster
