4. Using existing clusters
---------------------------------------------

It's possible to use this tool for testing providers that support Kubernetes as a Service. This means the provider offers the user a way for simply creating a cluster.
In case one wants to validate a provider that offers this and want to take advantage of it, simply skip steps 1.1 and 1.2 (install Terraform and manage ssh keys) and when running the test-suite, use option *--only-test* for normal -local results- run and *--via-backend* for verification runs.

**Note that you must have the file *~/.kube/config* for the previously provisioned cluster on your local machine so that it can be managed from there.**
