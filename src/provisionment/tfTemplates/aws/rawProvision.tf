provider "aws" {
  region                  = yamldecode(file(var.configsFile))["region"]
  shared_credentials_file = yamldecode(file(var.configsFile))["sharedCredentialsFile"]
}

resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

resource "aws_vpc" "vpc" {
  cidr_block = "172.16.0.0/16"
  tags = {
    Name = "tsvpc-${random_string.id.result}"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "tsigw-${random_string.id.result}"
  }
}

resource "aws_default_route_table" "drt" {
  default_route_table_id = aws_vpc.vpc.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_security_group" "tssg" { # this custom one is not assigned to the VMs, only the VPC's default one. Needs VM's vpc_security_group_ids
  name        = "tssg-${random_string.id.result}"
  vpc_id      = aws_vpc.vpc.id
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  tags = {
    Name = "tssg-${random_string.id.result}"
  }
}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "172.16.10.0/24"
  availability_zone = yamldecode(file(var.configsFile))["availabilityZone"]
  tags = {
    Name = "tssn-${random_string.id.result}"
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "tskp-${random_string.id.result}"
  public_key = file(yamldecode(file(var.configsFile))["pathToPubKey"])
}

resource "aws_instance" "kubenode" {
  depends_on = [aws_internet_gateway.igw]
  count         = var.customCount
  tags = {
    Name = "${var.instanceName}-${count.index}"
  }
  availability_zone = yamldecode(file(var.configsFile))["availabilityZone"]
  vpc_security_group_ids = [aws_security_group.tssg.id] # association
  instance_type = var.flavor
  ami      = yamldecode(file(var.configsFile))["ami"]
  key_name = aws_key_pair.deployer.key_name
  root_block_device {
    volume_size = var.storageCapacity
  }
  subnet_id = aws_subnet.subnet.id
  associate_public_ip_address = true
}
