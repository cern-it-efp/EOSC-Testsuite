3. Run
------------------------------

Once the configuration steps are completed, the Test-Suite is ready to be run:

.. code-block:: console

    EOSC-Testsuite$ chmod +x test_suite
    EOSC-Testsuite$ ./test_suite <options>

Once the provisionment steps are completed (Kubernetes cluster up and running) and pods are deployed, the run can be stopped by deleting all the pods.


Options
===============

-c, --configs
    Specifies custom location of configs.yaml. If not used, default will be the 'configurations' folder.

-t, --testsCatalog
    Specifies custom location of testsCatalog.yaml. If not used, default will be the 'configurations' folder.

--no-terraform
    Option to skip terraform provisionment, only ansible-playbook bootstrapping. To be used on providers that do not support terraform.

--only-test
    Run without creating the infrastructure (VMs and cluster), only deploy tests. Not valid for the first run.

.. --retry
..     In case of errors on the first run, use this option for retrying. This will make the test-suite try and reuse already provisioned infrastructure. Not valid for the first run, use only when VMs were provisioned but kubernetes bootstrapping failed.

--destroy <cluster>
    No test suite run, only destroy provisioned infrastructure. Argument can be: (note a quote wrapped and space separated subset of these can also be specified, for example "dlTest shared")

    'shared': Destroy the shared cluster.

    'dlTest': Destroy the GPU cluster.

    'hpcTest': Destroy the HPC cluster.

    'all': Destroy all clusters.

--destroy-on-completion <clusters>
    Destroy infrastructure once the test suite completes its run. Same arguments as for '--destroy' apply.

--custom-nodes <value>
    Set the number of instances that should be deployed for the shared cluster.


Other commands
==================

Once the test suite is running, you can view the Terraform provisionment logs by doing:

.. code-block:: console

    $ tail -f EOSC-Testsuite/logs


You can see the Ansible bootstrapping logs by doing:

.. code-block:: console

    $ tail -f EOSC-Testsuite/src/logging/ansibleLogs*


Once the bootstrapping has completed and tests are deployed, you can see the pods statuses by doing:

.. code-block:: console

    $ watch kubectl get pods --kubeconfig EOSC-Testsuite/src/tests/shared/config


If GPU and HPC tests were deployed, see their pods by doing:

.. code-block:: console

    $ watch kubectl --kubeconfig EOSC-Testsuite/src/tests/dlTest/config get pods # For GPU cluster
    $ watch kubectl --kubeconfig EOSC-Testsuite/src/tests/hpcTest/config get pods # For HPC cluster


Once the pods are deployed, the suite run can be stopped by destroying pods, useful for example when pods go "Evicted" or "ImagePullBackOff". Examples:

.. code-block:: console

    $ kubectl --kubeconfig EOSC-Testsuite/src/tests/shared/config delete pods --all # destroy all pods on the shared cluster
    $ kubectl --kubeconfig EOSC-Testsuite/src/tests/shared/config delete pod dodas-pod # destroy DODAS pod


The following aliases are available when using the provided Docker image:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Alias
     - Equivalence
   * - tfLogs
     - 'tail -f /EOSC-Testsuite/logs'
   * - ansibleLogs
     - 'tail -f /EOSC-Testsuite/src/logging/ansibleLogs*'
   * - watchPods
     - 'watch kubectl get pods --kubeconfig /EOSC-Testsuite/src/tests/shared/config -owide'
