from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "RegionCreateRequest",
    "RegionUpdateRequest",
    "RegionDeleteRequest",
    "RegionGetRequest",
    "RegionSearchQueryRequest",
    "RegionStatQueryRequest",
]

ResourceGroup = Literal["DOMAIN", "WORKSPACE"]


class RegionCreateRequest(BaseModel):
    name: str
    region_code: str
    provider: str
    tags: Union[dict, None] = None
    resource_group: ResourceGroup
    workspace_id: Union[str, None] = None
    domain_id: str


class RegionUpdateRequest(BaseModel):
    region_id: str
    name: str = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class RegionDeleteRequest(BaseModel):
    region_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class RegionGetRequest(BaseModel):
    region_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class RegionSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    region_id: Union[str, None] = None
    name: Union[str, None] = None
    region_code: Union[str, None] = None
    provider: Union[str, None] = None
    exists_only: Union[bool, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class RegionStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
