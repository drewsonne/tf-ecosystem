from functools import reduce

from tfeco.configuration_schema import ConfigSchema


class Composer(object):
    TAB_SPACES = 4

    def __init__(self, data, **facets):
        """
        :type facets: dict
        :type data: dict
        """
        self._data = data
        self._facets = facets

        ConfigSchema().load(self._data)

    def set_data(self, data):
        self._data = data

    def compose(self, fp):
        self._compose_backends(fp)
        self._compose_mappings(fp)
        self._compose_facets(fp)
        self._compose_providers(fp)

    def _compose_backends(self, fp):
        if 'backend' not in self._data:
            return
        backend_type = list(self._data['backend'].keys())[0]
        backend = self._data['backend'][backend_type]

        if 'key' in backend:
            backend['key'] = self._compose_backends_key()
            if backend['key'] is None:
                del backend['key']
            else:
                backend['key'] += '/state.tfstate'

        configuration = [
            self._build_config_line(kv, 2)
            for kv
            in backend.items()
        ]
        configuration.sort()

        fp.write("""terraform {{
    backend "{backend_type}" {{
{items}
    }}
}}""".format(
            backend_type=backend_type,
            items="\n".join(configuration)
        ))
        fp.write("\n\n")

    def _compose_mappings(self, fp):
        if 'mappings' not in self._data:
            return
        self._compose_locals(self._data['mappings'], fp)

    def _compose_locals(self, locals, fp):
        fp.write("locals {\n")
        mappings = []
        keys = list(locals.keys())
        keys.sort()
        for key in keys:
            local_entries = [
                self._build_config_line(kv, 2) for kv in locals[key].items()
            ]
            local_entries.sort()
            mappings.append("""    {name} = {{
{keys}
    }}""".format(
                name=key,
                keys="\n".join(local_entries)
            ))
        fp.write("\n\n".join(mappings))
        fp.write("\n}\n\n")

    def _compose_facets(self, fp):
        if 'facets' not in self._data:
            return
        state_facets = self._data['facets']['state']
        state_facets.sort()
        optional_facets = self._data['facets']['optional']
        optional_facets.sort()

        for facet in state_facets:
            fp.write("variable \"{name}\" {{".format(name=facet))
            if facet in self._facets:
                fp.write("\n    default = \"" + self._facets[facet] + "\"\n")
            elif facet in optional_facets:
                fp.write("\n    default = \"\"\n")
            fp.write("}\n\n")

    def _build_config_line(self, kv, indent=1, padding_width=1):
        key_padding = '{:' + str(padding_width) + '}'

        if type(kv[1]) == bool:
            key = "true" if kv[1] else "false"
        else:
            key = "\"" + kv[1] + "\""

        return "{indent}{key} = {value}".format(
            indent=" " * indent * self.TAB_SPACES,
            key=key_padding.format(kv[0]),
            value=key
        )

    def _build_block(self, configuration, indent=0):

        max_key_length = reduce(
            lambda key_length, key: max(key_length, len(key)),
            configuration.keys(),
            0
        )

        space_indent = " " * indent * self.TAB_SPACES
        block = "{\n"
        config_keys = list(configuration.keys())
        config_keys.sort()

        for key in config_keys:
            value = configuration[key]
            if type(value) == dict:
                key_padding = '{:' + str(max_key_length) + '}'
                block += " " * (indent + 1) * self.TAB_SPACES
                block += key_padding.format(key) + ' = '
                block += self._build_block(value, indent + 1)
            else:
                block += self._build_config_line(
                    [key, value],
                    indent + 1, max_key_length
                ) + "\n"

        block += space_indent + "}\n"

        return block

    def _compose_backends_key(self):
        if 'facets' not in self._data:
            return None

        facets = self._data['facets']
        if 'state' not in facets:
            return None

        state_facets = facets['state']
        state_facets.sort()

        filtered_state_facets = []
        for facet in state_facets:
            if facet in self._facets:
                value = self._facets[facet]
                if value != "":
                    filtered_state_facets.append(facet + '=' + value)

        if len(filtered_state_facets) == 0:
            return None

        return '/'.join(filtered_state_facets)

    def _compose_providers(self, fp):
        if 'providers' not in self._data:
            raise Exception("Missing Providers")

        providers = self._data['providers']
        provider_names = list(providers.keys())
        provider_names.sort()

        for name in provider_names:
            configurations = providers[name]
            for provider_instance in configurations:
                self._compose_provider(name, provider_instance, fp)

    def _compose_provider(self, name, provider_instance, fp):
        fp.write("provider \"" + name + "\" ")

        config_keys = list(provider_instance.keys())
        config_keys.sort()

        fp.write(self._build_block(provider_instance, 0))
