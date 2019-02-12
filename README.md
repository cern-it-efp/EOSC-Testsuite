# Test-Suite for cloud provider validation - CERN IT (EFP)

This tool is intended to be used for cloud providers (public cloud) validation and testing. The test-suite does 3 main things:

1) Create the infrastructure in which to deploy the tests: VMs are created using Terraform and then Kubernetes and Docker are installed on them to create a k8s cluster.

2) Deploy the tests: Docker images have been prebuilt and pushed to a hub/registry beforehand. These images are used on Kubernetes yaml file for the deployments.

3) Harvest results: at the end of each test run a results file -written in JSON- is created. This file is stored on the user’s machine, from where the test-suite was run.

*****

## Follow these steps to test a cloud provider:

## 1. Install Terraform
Terraform is the tool that creates the VMs that will later become a Kubernetes cluster. The test-suite makes use of it so download and install [Terraform](https://learn.hashicorp.com/terraform/getting-started/install.html).

## 2. Manage ssh keys
A ssh key pair is needed to establish connections to the VMs that will be created later. Therefore you must create (or import) this key on you provider beforehand and place the private key at `~/.ssh/id_rsa`.
Note errors may occur if your key doesn't have the right permissions. Set these to the right value using the following command:
```bash
chmod 600 path/to/key
```

## 3. Dependencies
This test-suite requires some packages to work properly and these must be installed by yourself.
### 3.1 Kubernetes client
In order to manage the Kubernetes cluster locally instead of using the master node, install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) on your machine.
### 3.2 Python
Python version 2.7 is required.

## 4. Test-suite download and preparation
### 4.1 Clone repo
Clone this repo as follows and cd into it:
```bash
git clone https://github.com/jyohhann/HNSciCloud-Testsuite.git
```
### 4.2 Prepare the suite according to your preferences and configurations
While completing this task refer to [Terraform's documentation](https://www.terraform.io/docs/providers/) in order to complete it successfully as some parts are provider specific and differ from one provider to another.  
You must fill configs.yaml to match your requirements, a filled example can be found in /config_examples.  
This file has different sections:

__`general`:__
For specifying general variables.

| Name	| Explanation / Values |
| ------------- | ---------------------- |
|slaves_amount | Indicate the number of slaves the cluster must contain |
|provider_name | Name of the provider |
|provider_instance_name | Compute instance name. This is provider specific. |
|path_to_key | Path to the location of your private key |


__`credentials`:__
For specifying the credentials to connect to the provider and deploy resources.

__`instance_definition`:__
In this section you should write all the key-pair values that would be written on the body of an instance declaration resource on Terraform, according to the provider you want to test. Refer to the documentation of the provider to check which pairs you need to specify and in any case you can run the test-suite (next steps) and if there is any missing pair a message will be shown on the console telling you which ones these are. This is how you must specify each pair:
```yaml
<YOUR_PROVIDER'S_STRING_FOR_A_KEY> = "<VALUE_GIVEN_FOR_THAT_KEY>"
```
An example (Exoscale):
```yaml
display_name = "kubenode"#NAME
template = "Linux CentOS 7.5 64-bit"
size = "GPU-small"
key_pair = "k_cl"
security_groups = ["kgroup"]
disk_size = 50
zone = "ch-gva-2"
```

Pay attention on this section to the name for the instance. A random string will be added later to the name given to the instance in order to avoid DNS issues when running the test-suite several times. For this, the block must contain the '#NAME' placeholder. When specifying the name for the instance, follow this structure:
```yaml
<YOUR_PROVIDER'S_STRING_FOR_NAME> = "<NAME_FOR_YOUR_INSTANCES>"#NAME
```
So lets image you provider's string for the instance name is "display_name", and you want to call your instances "kubenode" then you should write:
```yaml
display_name = "kubenode"#NAME
```
Note the '#NAME'!

**[Note: providers that do not support resource creation with Terraform can't be tested with this test-suite currently]**

__`tests_catalog`:__
In this section, you have to specify which tests you want to run. If you want to run certain test simply set its `run` variable to the True Boolean value. On the other hand if you don't want it to be run set this value to False. Following find a description of each test:

* Machine Learning using GPU: trains a GAN making use of a k8s cluster and MPI.

* S3 endpoint tests: An S3 test script that will check the following things

  - S3 authentication (access key + secret key)
  - PUT
  - GET
  - GET with prefix matching
  - GET chunk
  - GET multiple chunks

  For this test, besides the `run` variable, the following ones must be set on the configs.yaml file:

  | Name	| Explanation / Values |
  | ------------- | ---------------------- |
  |endpoint | Endpoint under which your S3 bucket is reachable. This URL must not include the bucket name but only the host. |

**[Note: If no test's `run` is set to True, this tool will simply create a raw Kubernetes cluster]**

## 5. Run the test-suite
Once all the previous steps are completed, the test-suite is ready to be run:
```bash
./test_suite.py <options>
```
Terraform will first show the user what it is going to do, what to create. If agreed, type "yes" and press enter.

### 5.1 Options
The following table describes all the accepted options:

| Name	| Explanation / Values |
| ------------- | ---------------------- |
|`--only-test` | When using this option the test-suite is run without creating the infrastructure (VMs and cluster) |

## 6. Results
Once all tests are run the results and logs of this cloud benchmarking can be seen at /results in JSON format.

*****

**This test-suite has been tested on:**  
Python: 2.7  
Linux distros: Ubuntu, Centos, Coreos, Debian, RedHat, Fedora  
OS running on provider's VMs : Centos  
Providers: Openstack, Exoscale  
