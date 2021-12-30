Layershift (Jelastic PaaS)
---------------------------------------------

Layershift specific variables for configs.yaml:

.. list-table::
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Explanation / Values
   * - nodes
     - Size of the cluster to create, including the master. (required)
   * - cores
     - Number of cores the cluster nodes should have. (required)
   * - tokenPath
     - Path to the file containing the token. See below the structure of such file. (required)
   * - podsOnMaster
     - If true, the taint on the master node will be removed so pods can run there. (required)


Credentials file's structure:

.. code-block:: console

  token: e3ca3e7620f7e0de1b7cd7a2



Create and configure cluster:

.. code-block:: console

    $ python3 main.py -c ../../../../examples/layershift/configs.yaml

On success, the cluster is ready and the test suite can be run, using the same configs file and the option *--onlyTest*.


Destroy cluster:

.. code-block:: console

    $ python3 main.py -d -c ../../../../examples/layershift/configs.yaml
