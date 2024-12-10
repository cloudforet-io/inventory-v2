from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class Region(MongoModel):
    region_id = StringField(max_length=40, unique=True)
    name = StringField(max_length=255)
    region_code = StringField(max_length=255)
    provider = StringField(max_length=255)
    tags = DictField()
    resource_group = StringField(max_length=40, choices=("DOMAIN", "WORKSPACE"))
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": ["name", "tags", "updated_at"],
        "minimal_fields": ["region_id", "name", "region_code", "provider"],
        "ordering": ["name"],
        "indexes": [
            "provider",
            "resource_group",
            "workspace_id",
            "domain_id",
        ],
    }
