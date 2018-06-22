import typing


class Composer(object):
    def __init__(self, data, **facets):
        self._data = data
        self._facets = facets

    def set_data(self, data):
        self._data = data

    def compose(self, fp: typing.TextIO):
        self._compose_backends(fp)
        self._compose_mappings(fp)
        self._compose_facets(fp)

    def _compose_backends(self, fp: typing.TextIO):
        if 'backend' not in self._data:
            return
        backend_type = list(self._data['backend'].keys())[0]
        backend = self._data['backend'][backend_type]

        if 'key' in backend:
            backend['key'] = self._compose_backends_key(
                backend['key']) + '/state.tfstate'

        configuration = [self._config_line(kv, 2) for kv in backend.items()]

        fp.write("""terraform {{
    backend "{backend_type}" {{
{items}
    }}
}}""".format(
            backend_type=backend_type,
            items="\n".join(configuration)
        ))
        fp.write("\n\n")

    def _compose_mappings(self, fp: typing.TextIO):
        if 'mappings' not in self._data:
            return
        self._compose_locals(self._data['mappings'], fp)

    def _compose_locals(self, locals, fp: typing.TextIO):
        fp.write("locals {\n")
        mappings = []
        for name, mapping in locals.items():
            local_entries = [self._config_line(kv, 2) for kv in mapping.items()]
            mappings.append("""    {name} = {{
{keys}
    }}""".format(
                name=name,
                keys="\n".join(local_entries)
            ))
        fp.write("\n\n".join(mappings))
        fp.write("\n}\n\n")

    def _compose_facets(self, fp: typing.TextIO):
        if 'facets' not in self._data:
            return
        state_facets = self._data['facets']['state']
        optional_facets = self._data['facets']['optional']

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

    def _compose_backends_key(self, keys):
        state_facets = self._data['facets']['state']

        # for facet_key, facet_value in facets.items():
        #     if facet_value != "":
        #         if

        filtered_state_facets = {}
        for facet in state_facets:
            if facet in self._facets:
                value = self._facets[facet]
                if value != "":
                    filtered_state_facets[facet] = value

        return '/'.join([
            kv[0] + '=' + kv[1]
            for kv
            in filtered_state_facets.items()
        ])
