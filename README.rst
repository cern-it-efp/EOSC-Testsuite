================================================
OCRE Test-Suite for cloud validation - CERN
================================================

This tool is intended to be used for cloud services validation and testing across the stack.
Please find the the repository here: https://github.com/cern-it-efp/OCRE-Testsuite
The latest documentation can be found here: https://ocre-testsuite.readthedocs.io/en/latest/

The test-suite executes four main steps:

1) Infrastructure provisioning: VMs are created using Terraform and then Kubernetes and Docker are installed on them to create a k8s cluster.

2) Deploy the tests: Kubernetes resource definition files (YAML) are used to deploy the tests, either as single pods or deployments.

3) Harvest results: at the end of each test run a result file -written in JSON- is created. This file is stored locally.

4) Through a verification system, the Test-Suite can also be triggered from a service running at CERN. In this case, results are then pushed to a S3 Bucket at CERN.

The test set described below is based on the tests used in `Helix Nebula The Science Cloud <https://www.hnscicloud.eu/>`_ PCP project funded by the European Commission.

The developers would like to thank to all test owners and contributors to this project.

**This test-suite has been tested on:**

+------------------------------+---------------------------------------------------------------------------------+
|Python                        | 3                                                                               |
+------------------------------+---------------------------------------------------------------------------------+
|Linux distros                 | Ubuntu, Centos, Coreos, Debian, RedHat, Fedora                                  |
+------------------------------+---------------------------------------------------------------------------------+
|OS running on provider's VMs  | Centos7                                                                         |
+------------------------------+---------------------------------------------------------------------------------+
|Providers                     | | Exoscale (Cloudstack)                                                         |
|                              | | CERN Private Cloud (OpenStack)                                                |
|                              | | Cloudscale (OpenStack)                                                        |
+------------------------------+---------------------------------------------------------------------------------+

The test suite is being tested in several additional cloud providers. As tests are concluded the cloud providers names will be added in the table above.

.. header-end

*****

Documentation
---------------------------------------------
Find the full documentation at `ocre-testsuite.rtfd.io <https://ocre-testsuite.readthedocs.io/en/latest/>`_

.. license-start

License
---------------------------------------------
Copyright (C) CERN.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see `gnu.org/licenses <https://www.gnu.org/licenses/>`_.

.. license-end

.. image:: img/logo.jpg
   :height: 20px
   :width: 20px
   :scale: 20
   :target: https://home.cern/
   :alt: CERN logo
