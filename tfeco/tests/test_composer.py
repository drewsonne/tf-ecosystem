from io import StringIO
from unittest import TestCase

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
        bucket = "my-bucket"
        region = "bucket_region"
        acl = "bucket_acl"
        dynamodb_table = "dynammodb_table"
        role_arn = "role_arn"
        key = "bucket_key"
    }
}

locals {
    account-names = {
        test = "012345678901"
        stage = "234567890123"
        live = "456789012345"
    }
}

variable "account" {
    default = ""
}

variable "region" {}

variable "environment" {}

variable "stack" {}

""", mockIO.read())

    def test__compose_backends(self):
        c = Composer({
            'backend': {
                's3': {
                    'bucket': 'my-bucket',
                    'region': 'bucket_region',
                    'acl': 'bucket_acl',
                    'dynamodb_table': 'dynammodb_table',
                    'role_arn': 'role_arn',
                    'key': 'bucket_key'
                }
            }
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""terraform {
    backend "s3" {
        bucket = "my-bucket"
        region = "bucket_region"
        acl = "bucket_acl"
        dynamodb_table = "dynammodb_table"
        role_arn = "role_arn"
        key = "bucket_key"
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
            }
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""locals {
    account-names = {
        test = "012345678901"
        stage = "234567890123"
        live = "456789012345"
    }

    randoms = {
        foo = "bar"
        hello = "world"
    }
}

""", mockIO.read())

    def test__compose_facets(self):
        c = Composer({
            'facets': {
                'state': ['hello', 'world', 'foo', 'bar'],
                'optional': ['foo', 'bar']
            }
        })

        mockIO = StringIO()

        c.compose(mockIO)

        mockIO.seek(0)

        self.assertEqual("""variable "hello" {}

variable "world" {}

variable "foo" {
    default = ""
}

variable "bar" {
    default = ""
}

""", mockIO.read())

    def test__compose_backends_key(self):
        c = Composer({
            'facets': {
                'state': ['test_key', 'missing_key']
            },
        }, test_key='mock')

        key_path = c._compose_backends_key(None)

        self.assertEqual(key_path, 'test_key=mock')
