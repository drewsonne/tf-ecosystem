from pathlib import Path

from tfeco.configuration_schema import ConfigSchema
import pyaml
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class ConfigurationLoader(object):

    def __init__(self):
        self._config = {}
        self._config_folder = Path(Path.home(), '.config', 'tf-ecosystem')
        self._config_file = Path(self._config_folder, 'config.ini')

    def load(self) -> 'ConfigurationLoader':
        if not self._config_folder.exists():
            self._config_folder.mkdir()

        self._init_defaults()

        if self._config_file.exists():
            with self._config_file.open('r') as fp:
                self._config = yaml.load(fp, Loader=Loader)
                ConfigSchema().load(self._config)

        return self

    def save(self) -> 'ConfigurationLoader':
        with self._config_file.open('w') as fp:
            pyaml.dump(self._config, fp)

        return self

    def _init_defaults(self):
        if self._config is None or len(self._config) == 0:
            self._config = {
                'facets': {
                    'state': [
                        'account',
                        'region',
                        'environment',
                        'stack'
                    ],
                    'optional': ['account']
                },
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
                'mappings': {
                    'account-names': {
                        'test': '012345678901',
                        'stage': '234567890123',
                        'live': '456789012345'
                    }
                },
                'providers': {
                    'aws': []
                }
            }
