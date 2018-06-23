from tfeco.configuration_schema import ConfigSchema


class Composer(object):
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

        configuration = [self._config_line(kv, 2) for kv in backend.items()]
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
                self._config_line(kv, 2) for kv in locals[key].items()
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

    def _config_line(self, kv, indent=1):
        return "{indent}{key} = \"{value}\"".format(
            indent=" " * indent * 4,
            key=kv[0],
            value=kv[1]
        )

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
