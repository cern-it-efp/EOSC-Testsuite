3. Run
------------------------------

Once the configuration steps are completed, the Test-Suite is ready to be run:

.. code-block:: console

    EOSC-Testsuite$ chmod +x test_suite
    EOSC-Testsuite$ ./test_suite <options>

The suite uses a combination of Linux' watch and cat commands to display the logs of the run. Hence, the suite will fail if no terminal/TTY is available.
To change this behaviour use the option *noWatch* as defined in the options below.

Once the provisionment steps are completed (Kubernetes cluster up and running) and pods are deployed, the run will finish once all the deployed tests complete.
If for any reason you want to stop the run before completion, delete all the pods and this will finish the run.


Options
===============

-c, --configs
    Specifies a custom location of the general configurations YAML file. If omitted, EOSC-Testsuite/configs.yaml will be used.

-t, --testsCatalog
    Specifies a custom location of the tests catalog YAML file. If omitted, EOSC-Testsuite/testsCatalog.yaml will be used.

--noTerraform
    Option to skip terraform provisionment, only ansible-playbook bootstrapping. To be used on providers that do not support terraform.

-o, --onlyTest
    Run without creating the infrastructure (VMs and cluster), only deploy tests. Not valid for the first run.

.. --retry
..     In case of errors on the first run, use this option for retrying. This will make the test-suite try and reuse already provisioned infrastructure. Not valid for the first run, use only when VMs were provisioned but kubernetes bootstrapping failed.

--destroy <cluster>
    No test suite run, only destroy provisioned infrastructure. Argument can be: (note a quote wrapped and space separated subset of these can also be specified, for example "dlTest shared")

    'shared': Destroy the shared cluster.

    'dlTest': Destroy the GPU cluster.

    'hpcTest': Destroy the HPC cluster.

    'all': Destroy all clusters.

--destroyOnCompletion <clusters>
    Destroy infrastructure once the test suite completes its run. Same arguments as for '--destroy' apply.

--customNodes <value>
    Set the number of instances that should be deployed for the shared cluster. If omitted, the suite will provision as many nodes as tests of the general ones (s3Test, dataRepatriationTest, cpuBenchmarking, perfsonarTest and dodasTest) were selected.

--usePrivateIPs
    By default the test suite signs the cluster's certificate for the master's NAT IP address.
    This is required in order to be able to communicate with the cluster through the internet because in most of the cases, providers do not allocate public IPs to the VMs (no network interfaces with public IP) but use NAT.
    If this option is used, the test suite will not sign the certificate for the master's NAT IP address.This means, the cluster can be reached only from the network it is connected to.
    For this scenario, a bastion VM should be used.

    When using the docker approach, *--net=host* should be used in the Docker run command. With that option, the container will use the network used by its host.
    Without it, the container wouldn't be able to communicate with the nodes, as it would not be in the same network as them and the nodes will not have public IPs.

--noWatch
    Makes the test suite not use the watch function, hence disabling logs.

--freeMaster
    Disables running pods (tests and/or benchmarks) on the master node.
    For the shared and proGAN's clusters, an extra node would be added. For example, if 3 tests were selected, 4 nodes would be created.
    For the other clusters, the number of nodes created would still be the one the user specified on the tests catalog YAML file.

--publish
    Upload results to CERN's S3. More information can be found here.


Other commands
==================

This sections provides a set of commands that can be used to obtain logs and in general, check the status of the run.
Note all these assume the location is EOSC-Testsuite, this is, inside the cloned repository.

Once the test suite is running, you can view the Terraform provisionment logs by doing:

.. code-block:: console

    $ tail -f EOSC-Testsuite/logs


You can see the Ansible bootstrapping logs by doing:

.. code-block:: console

    $ tail -f EOSC-Testsuite/src/logging/ansibleLogs*


Once the bootstrapping has completed and tests are deployed, you can see the pods statuses by doing:

.. code-block:: console

    $ watch kubectl get pods --kubeconfig EOSC-Testsuite/src/tests/shared/config


For tests other than those that are deployed in the general cluster, see their pods by doing:

.. code-block:: console

    $ watch kubectl --kubeconfig EOSC-Testsuite/src/tests/dlTest/config get pods # For dlTest cluster
    $ watch kubectl --kubeconfig EOSC-Testsuite/src/tests/dlTest/config get pods # For proGANTest cluster
    $ watch kubectl --kubeconfig EOSC-Testsuite/src/tests/hpcTest/config get pods # For hpcTest cluster

Once the pods are deployed, the suite run can be stopped by destroying pods. This is useful for example when pods go "Evicted" or "ImagePullBackOff". Examples:

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
