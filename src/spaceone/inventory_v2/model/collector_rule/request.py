from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "CollectorRuleCreateRequest",
    "CollectorRuleUpdateRequest",
    "CollectorRuleDeleteRequest",
    "CollectorRuleGetRequest",
    "CollectorRuleChangeOrderRequest",
    "CollectorRuleSearchQueryRequest",
    "CollectorRuleStatQueryRequest",
]

ResourceGroup = Literal["DOMAIN", "WORKSPACE"]


class CollectorRuleCreateRequest(BaseModel):
    collector_id: str
    name: Union[str, None] = None
    conditions: Union[list, None] = None
    conditions_policy: str
    actions: dict
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class CollectorRuleUpdateRequest(BaseModel):
    collector_rule_id: str
    name: Union[str, None] = None
    conditions: Union[list, None] = None
    conditions_policy: Union[str, None] = None
    actions: Union[dict, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class CollectorRuleDeleteRequest(BaseModel):
    collector_rule_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class CollectorRuleGetRequest(BaseModel):
    collector_rule_id: str
    workspace_id: Union[list, str, None] = None
    domain_id: str


class CollectorRuleChangeOrderRequest(BaseModel):
    collector_rule_id: str
    order: int
    workspace_id: Union[str, None] = None
    domain_id: str


class CollectorRuleSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    collector_rule_id: Union[str, None] = None
    name: Union[str, None] = None
    rule_type: Union[str, None] = None
    collector_id: Union[str, None] = None
    workspace_id: Union[list, str, None] = None
    domain_id: str


class CollectorRuleStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[list, str, None] = None
    domain_id: str
