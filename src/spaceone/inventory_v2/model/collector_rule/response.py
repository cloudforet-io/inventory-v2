from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.core import utils

__all__ = ["CollectorRuleResponse", "CollectorRulesResponse"]


class CollectorRuleResponse(BaseModel):
    collector_rule_id: Union[str, None] = None
    name: Union[str, None] = None
    rule_type: Union[str, None] = None
    order: Union[int, None] = None
    conditions: Union[list, None] = None
    conditions_policy: Union[str, None] = None
    actions: Union[dict, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    collector_id: Union[str, None] = None
    resource_group: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class CollectorRulesResponse(BaseModel):
    results: List[CollectorRuleResponse]
    total_count: int
