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

        fp.write(
            """terraform {{\n    backend "{btype}" {items}}}""".format(
                btype=backend_type,
                items=self._build_block(backend, 1)
            ))
        fp.write("\n\n")

    def _compose_mappings(self, fp):
        mappings = self._data['mappings'] if 'mappings' in self._data else {}
        self._compose_locals(mappings, fp)

    def _compose_locals(self, locals, fp):
        keys = list(locals.keys())
        if len(keys):
            fp.write("locals {\n")
            mappings = []
            keys.sort()
            for key in keys:
                mappings.append("""    {name} = {keys}""".format(
                    name=key,
                    keys=self._build_block(locals[key], 1)
                ))
            fp.write("\n".join(mappings))
            fp.write("}\n\n")

    def _compose_facets(self, fp):
        facets = self._data['facets'] if 'facets' in self._data else {
            'state': [],
            'optional': []
        }
        state_facets = facets['state'] if 'state' in facets else []

        if 'composite' in facets:
            for composite_key, composite_parts in facets['composite'].items():
                # state_facets.remove(composite_key)
                for part in composite_parts:
                    state_facets.append(part)
        state_facets = list(set(state_facets))

        state_facets.sort()
        optional_facets = facets['optional'] if 'optional' in facets else []
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
            key = "\"" + str(kv[1]) + "\""

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

        facets = self._data['facets'] if 'facets' in self._data else {
            'state': []
        }

        state_facets = facets['state']

        ignore_facets = []

        composite_state_facets = []
        if 'composite' in facets:
            for composite_key, composite_parts in facets['composite'].items():
                if composite_key in state_facets:
                    state_facets.remove(composite_key)
                component_values = []
                for part in composite_parts:
                    ignore_facets.append(part)
                    state_facets.append(part)
                    component_values.append(self._facets[part])
                composite_state_facets.append(
                    composite_key + '=' + '/'.join(component_values)
                )

        filtered_state_facets = []
        for facet in state_facets:
            if facet in self._facets:
                if facet not in ignore_facets:
                    value = self._facets[facet]
                    if value != "":
                        filtered_state_facets.append(facet + '=' + value)

        if len(filtered_state_facets) == 0:
            return None

        filtered_state_facets.sort()

        return '/'.join(filtered_state_facets + composite_state_facets)

    def _compose_providers(self, fp):
        providers = self._data['providers'] \
            if 'providers' in self._data \
            else {}
        provider_names = list(providers.keys())
        provider_names.sort()

        for name in provider_names:
            configurations = providers[name]
            for provider_instance in configurations:
                self._compose_provider(name, provider_instance, fp)
                # fp.write("\n\n")

    def _compose_provider(self, name, provider_instance, fp):
        fp.write("provider \"" + name + "\" ")

        config_keys = list(provider_instance.keys())
        config_keys.sort()

        fp.write(self._build_block(provider_instance, 0) + "\n")
