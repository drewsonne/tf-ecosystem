from tfeco.configuration_loader import ConfigurationLoader

from tfeco.composer import Composer


class ConfigurationFile(ConfigurationLoader):
    """
    Describes a file path to the configuration for the utility
    """

    def __init__(self):
        super().__init__()
        self._config = {
            'facets': {'state': [], 'optional': []}
        }

    def facets(self):
        states = self._config['facets']['state']
        optional = self._config['facets']['optional']

        for state in states:
            yield state, state in optional

    def composer(self, **facets) -> Composer:
        return Composer(self._config, **facets)
