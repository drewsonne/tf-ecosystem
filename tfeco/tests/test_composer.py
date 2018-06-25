from unittest import TestCase

from io import StringIO

from tfeco.composer import Composer
from tfeco.configuration import ConfigurationFile


class TestComposer(TestCase):

    def test__compose_defaults(self):
        cfg = ConfigurationFile()
        cfg._init_defaults()
        c = Composer(cfg._config)

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""terraform {
    backend "s3" {
        acl            = "bucket_acl"
        bucket         = "my-bucket"
        dynamodb_table = "dynamodb_table"
        region         = "us-east-1"
        role_arn       = "role_arn"
    }
}

locals {
    account-names = {
        live  = "456789012345"
        stage = "234567890123"
        test  = "012345678901"
    }
}

variable "account" {
    default = ""
}

variable "environment" {}

variable "region" {}

variable "stack" {}

""", mockIO.read())

    def test__compose_backends(self):
        c = Composer({
            'backend': {
                's3': {
                    'bucket': 'my-bucket',
                    'region': 'bucket_region',
                    'acl': 'bucket_acl',
                    'dynamodb_table': 'dynamodb_table',
                    'role_arn': 'role_arn',
                    'key': 'bucket_key'
                }
            },
            'providers': {}
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""terraform {
    backend "s3" {
        acl            = "bucket_acl"
        bucket         = "my-bucket"
        dynamodb_table = "dynamodb_table"
        region         = "bucket_region"
        role_arn       = "role_arn"
    }
}

""", mockIO.read())

    def test__compose_mappings(self):
        c = Composer({
            'mappings': {
                'account-names': {
                    'test': '012345678901',
                    'stage': '234567890123',
                    'live': '456789012345'
                },
                'randoms': {
                    'foo': 'bar',
                    'hello': 'world'
                }
            },
            'providers': {}
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""locals {
    account-names = {
        live  = "456789012345"
        stage = "234567890123"
        test  = "012345678901"
    }

    randoms = {
        foo   = "bar"
        hello = "world"
    }
}

""", mockIO.read())

    def test__compose_facets(self):
        c = Composer({
            'facets': {
                'state': ['hello', 'world', 'foo', 'bar'],
                'optional': ['foo', 'bar']
            },
            'providers': {}
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""variable "bar" {
    default = ""
}

variable "foo" {
    default = ""
}

variable "hello" {}

variable "world" {}

""", mockIO.read())

    def test__compose_backends_key(self):
        c = Composer({
            'facets': {
                'state': ['test_key', 'missing_key']
            },
        }, test_key='mock')

        key_path = c._compose_backends_key()

        self.assertEqual(key_path, 'test_key=mock')

    def test__compose_providers(self):
        c = Composer({
            'providers': {
                'aws': [{
                    "region": "${var.region}",
                    "skip_get_ec2_platforms": True,
                    "assume_role": {
                        "role_arn": "arn:aws:iam::${lookup("
                                    "var.account-names, "
                                    "var.account"
                                    ")}:role/${var.environment}"
                                    "-terraform-provisioner",
                        "session_name": "${terraform.env}-${replace("
                                        "var.stack,"
                                        "\"/[^\\w\\d-]/\",\"\")}"
                                        "-terraform"
                    }
                }]
            }
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""provider "aws" {
    assume_role            = {
        role_arn     = "arn:aws:iam::${lookup(var.account-names, var.account)}:role/${var.environment}-terraform-provisioner"
        session_name = "${terraform.env}-${replace(var.stack,"/[^\\w\\d-]/","")}-terraform"
    }
    region                 = "${var.region}"
    skip_get_ec2_platforms = true
}

""", mockIO.read())

    def test__compose_block(self):
        c = Composer({})
        block = c._build_block({
            'one': 'foo',
            'two': 'bar',
            'three': 'hello',
            'four': 'world'
        })

        self.assertEqual("""{
    four  = "world"
    one   = "foo"
    three = "hello"
    two   = "bar"
}
""", block)

    def test__compose_block_dict(self):
        c = Composer({})
        block = c._build_block({
            'one': 'foo',
            'two': 'bar',
            'three': 'hello',
            'four': {
                'five': 'world',
                'six': 'the',
                'seven': 'world',
                'eight': 'is'
            }
        })

        self.assertEqual("""{
    four  = {
        eight = "is"
        five  = "world"
        seven = "world"
        six   = "the"
    }
    one   = "foo"
    three = "hello"
    two   = "bar"
}
""", block)

    def test__composite_facet(self):
        c = Composer({
            'backend': {
                's3': {
                    'bucket': 'my-bucket',
                    'region': 'us-east-1',
                    'acl': 'bucket_acl',
                    'dynamodb_table': 'dynamodb_table',
                    'role_arn': 'role_arn',
                    'key': 'bucket_key'
                }
            },
            'facets': {
                'state': ['env', 'comp_stack'],
                'composite': {
                    "comp_stack": ['stack', 'substack']
                }
            }
        }, env='live', stack='mock_stack', substack='mock_substack')

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""terraform {
    backend "s3" {
        acl            = "bucket_acl"
        bucket         = "my-bucket"
        dynamodb_table = "dynamodb_table"
        key            = "env=live/comp_stack=mock_stack/mock_substack/state.tfstate"
        region         = "us-east-1"
        role_arn       = "role_arn"
    }
}

variable "env" {
    default = "live"
}

variable "stack" {
    default = "mock_stack"
}

variable "substack" {
    default = "mock_substack"
}

""", mockIO.read())
