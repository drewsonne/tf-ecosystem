terraform {
    backend "s3" {
        acl = "bucket_acl"
        bucket = "my-bucket"
        dynamodb_table = "dynammodb_table"
        key = "account=beamly-rd/environment=test/region=eu-central-1/stack=mip-profile-engine/state.tfstate"
        region = "bucket_region"
        role_arn = "role_arn"
    }
}

locals {
    account-names = {
        live = "456789012345"
        stage = "234567890123"
        test = "012345678901"
    }
}

variable "account" {
    default = "beamly-rd"
}

variable "environment" {
    default = "test"
}

variable "region" {
    default = "eu-central-1"
}

variable "stack" {
    default = "mip-profile-engine"
}

provider "aws" {
    assume_role = "{'role_arn': 'arn:aws:iam::${lookup(var.account-names, var.account)}:role/${var.environment}-terraform-provisioner'}"
    region = "${var.region}"
    skip_get_ec2_platforms = "True"
}

provider "gocd" {
    baseurl = "http://goserver.go.beamly.com:8153/go/"
    password = "notifications"
    skip_ssl_check = "True"
    username = "notifications"
}

