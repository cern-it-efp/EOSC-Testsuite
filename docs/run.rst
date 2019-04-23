3. Run the test-suite
------------------------------

Once the previous configuration steps are completed, the Test-Suite is ready to be run:

.. code-block:: console

    $ ./test_suite.py <options>

Terraform will first show the user what will be done and what to create. If agreed, type "yes" and press enter.

Options
===============
The following table describes all the available options:

+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
|Name              | Explanation / Values                                                                                                                                           |
+==================+================================================================================================================================================================+
|--only-test       | | Run without creating the infrastructure (VMs and cluster), only deploy tests.                                                                                |
|                  | | Not valid for the first run.                                                                                                                                 |
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
|--auto-retry      | | Automatically retry in case of errors on the Terraform phase.                                                                                                |
|                  | | Note that in the case errors occur, the user will have to stop the run using Ctrl+Z.                                                                         |
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
|--via-backend     | | Runs the Test-Suite using CERN's backend service instead of the cloned local version.                                                                        |
|                  | | This option must be used for verification purposes (2nd or later runs).                                                                                      |
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
