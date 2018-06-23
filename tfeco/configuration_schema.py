from marshmallow import Schema, fields


class ConfigFacetSchema(Schema):
    state = fields.List(fields.String)
    optional = fields.List(fields.String)


class ConfigSchema(Schema):
    facets = fields.Nested(ConfigFacetSchema)
    backend = fields.Dict()
    mappings = fields.Dict()
    providers = fields.Dict()
