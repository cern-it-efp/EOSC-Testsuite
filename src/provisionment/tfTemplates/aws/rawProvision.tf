provider "aws" {
  region                  = yamldecode(file(var.configsFile))["region"]
  shared_credentials_file = yamldecode(file(var.configsFile))["sharedCredentialsFile"]
}

# TODO: tried this and also creating a VM by hand (using this VPC) whith the traffic completelly opened and still didnt work.
#       Try the whole thing by hand (via UI) create VPC with subnet, VM, etc

# NOTE: On my account, I was always using the same VPC (default one) and on that one I had opened once the firewall, that's why I never had to do that again and never had problems because that firewall was the default VPC's firewall so it was all okay there


resource "aws_vpc" "vpc" { # TODO: the VPC actually creates a default security group that allows all traffic coming from itself (source of the rule is its own ID)
  cidr_block = "172.16.0.0/16"
  tags = {
    Name = "tsvpc"
  }
}

#resource "aws_security_group" "tssg" { # TODO: this custome one is not assigned to the VMs, only the VPC's default one
#  name        = "tssg"
#  vpc_id      = aws_vpc.vpc.id
#
#  ingress {
#    description = "SSH"
#    from_port   = 22
#    to_port     = 22
#    protocol    = "tcp"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#  ingress {
#    description = "K8s API"
#    from_port   = 6443
#    to_port     = 6443
#    protocol    = "tcp"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#  ingress {
#    description = "Node access API"
#    from_port   = 10250
#    to_port     = 10250
#    protocol    = "tcp"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#  ingress {
#    description = "Flannel network"
#    from_port   = 8472
#    to_port     = 8472
#    protocol    = "udp"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#
#  egress {
#    from_port   = 0
#    to_port     = 0
#    protocol    = "-1"
#    cidr_blocks = ["0.0.0.0/0"]
#  }
#  tags = {
#    Name = "tssg"
#  }
#}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "172.16.10.0/24"
  #availability_zone = "us-west-2a"
  tags = {
    Name = "tssn"
  }
}

resource "aws_instance" "kubenode" {
  count         = var.customCount
  tags = {
    Name = "${var.instanceName}-${count.index}"
  }
  security_groups = var.securityGroups
  instance_type = var.flavor
  ami      = yamldecode(file(var.configsFile))["ami"]
  key_name = yamldecode(file(var.configsFile))["keyName"]
  root_block_device {
    volume_size = var.storageCapacity
  }
  subnet_id = aws_subnet.subnet.id
  associate_public_ip_address = true
}
