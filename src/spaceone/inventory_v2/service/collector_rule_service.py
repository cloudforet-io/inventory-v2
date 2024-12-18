import logging
import fnmatch
from typing import Union

from spaceone.core.error import *
from spaceone.core.service import *

from spaceone.inventory_v2.error.collector_rule import *
from spaceone.inventory_v2.manager.collector_rule_manager import CollectorRuleManager
from spaceone.inventory_v2.manager.collector_manager import CollectorManager
from spaceone.inventory_v2.manager.identity_manager import IdentityManager
from spaceone.inventory_v2.model.collector_rule.request import *
from spaceone.inventory_v2.model.collector_rule.response import *
from spaceone.inventory_v2.model.collector_rule.database import CollectorRule

__LOGGER = logging.getLogger(__name__)

_SUPPORTED_CONDITION_KEYS = [
    "provider",
    "cloud_service_group",
    "cloud_service_type",
    "region_code",
    "account",
    "reference.resource_id",
    "data.<key>",
    "tags.<key>",
]
_SUPPORTED_CONDITION_OPERATORS = ["eq", "contain", "not", "not_contain"]


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class CollectorRuleService(BaseService):
    resource = "CollectorRule"

    def __init__(self, metadata):
        super().__init__(metadata)
        self.collector_rule_mgr = CollectorRuleManager()

    @transaction(
        permission="inventory-v2:CollectorRule.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def create(
        self, params: CollectorRuleCreateRequest
    ) -> Union[CollectorRuleResponse, dict]:
        """Create Collector rule

        Args:
            params (dict): {
                'collector_id': 'str',          # required
                'name': 'str',
                'conditions': 'list',
                'conditions_policy': 'str',     # required
                'actions': 'dict',              # required
                'options': 'dict',
                'tags': 'dict',
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth (required)
            }

        Returns:
            CollectorRuleResponse:
        """

        collector_mgr = CollectorManager()

        domain_id = params.domain_id
        workspace_id = params.workspace_id
        collector_id = params.collector_id
        conditions = params.conditions or []
        conditions_policy = params.conditions_policy
        actions = params.actions

        collector_vo = collector_mgr.get_collector(
            collector_id, domain_id, workspace_id
        )

        params_dict = params.dict()
        params_dict["collector"] = collector_vo
        params_dict["rule_type"] = "CUSTOM"
        params_dict["resource_group"] = collector_vo.resource_group

        # Check permission by resource group
        if params_dict["resource_group"] == "WORKSPACE":
            if workspace_id is None:
                raise ERROR_REQUIRED_PARAMETER(key="workspace_id")

            identity_mgr = IdentityManager()
            identity_mgr.check_workspace(workspace_id, domain_id)
        else:
            params_dict["workspace_id"] = "*"

        if conditions_policy == "ALWAYS":
            params_dict["conditions"] = []
        else:
            if len(conditions) == 0:
                raise ERROR_REQUIRED_PARAMETER(key="conditions")
            else:
                self._check_conditions(conditions)

        self._check_actions(actions, domain_id)

        params_dict["order"] = (
            self._get_highest_order(collector_id, params_dict["rule_type"], domain_id)
            + 1
        )

        collector_rule_vo = self.collector_rule_mgr.create_collector_rule(params_dict)

        return CollectorRuleResponse(**collector_rule_vo.to_dict())

    @transaction(
        permission="inventory-v2:CollectorRule.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def update(
        self, params: CollectorRuleUpdateRequest
    ) -> Union[CollectorRuleResponse, dict]:
        """Update collector rule
        Args:
            params (dict): {
                'collector_rule_id': 'str',     # required
                'name': 'str',
                'conditions': 'list',
                'conditions_policy': 'str',
                'actions': 'dict',
                'options': 'dict'
                'tags': 'dict'
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
            CollectorRuleResponse:
        """

        collector_rule_id = params.collector_rule_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id

        conditions_policy = params.conditions_policy
        conditions = params.conditions or []

        actions = params.actions

        collector_rule_vo = self.collector_rule_mgr.get_collector_rule(
            collector_rule_id, domain_id, workspace_id
        )

        params_dict = params.dict(exclude_unset=True)
        print(params_dict)

        if collector_rule_vo.rule_type == "MANAGED":
            raise ERROR_NOT_ALLOWED_TO_UPDATE_RULE()

        if conditions_policy:
            if conditions_policy == "ALWAYS":
                params_dict["conditions"] = []
            else:
                if len(conditions) == 0:
                    raise ERROR_REQUIRED_PARAMETER(key="conditions")
                else:
                    self._check_conditions(conditions)

        if actions:
            self._check_actions(actions, domain_id)

        collector_rule_vo = self.collector_rule_mgr.update_collector_rule_by_vo(
            params_dict, collector_rule_vo
        )

        return CollectorRuleResponse(**collector_rule_vo.to_dict())

    @transaction(
        permission="inventory-v2:CollectorRule.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def change_order(
        self, params: CollectorRuleChangeOrderRequest
    ) -> Union[CollectorRuleResponse, dict]:
        """Change collector rule's order

        Args:
            params (dict): {
                'collector_rule_id': 'str',     # required
                'order': 'int',                 # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
            CollectorRuleResponse:
        """

        collector_rule_id = params.collector_rule_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        order = params.order

        target_rule_vo: CollectorRule = self.collector_rule_mgr.get_collector_rule(
            collector_rule_id, domain_id, workspace_id
        )

        self._check_order(order)

        if target_rule_vo.rule_type == "MANAGED":
            raise ERROR_NOT_ALLOWED_TO_CHANGE_ORDER()

        if target_rule_vo.order == order:
            return CollectorRuleResponse(**target_rule_vo.to_dict())

        highest_order = self._get_highest_order(
            target_rule_vo.collector_id,
            target_rule_vo.rule_type,
            target_rule_vo.domain_id,
        )

        if order > highest_order:
            raise ERROR_INVALID_PARAMETER(
                key="order",
                reason=f"There is no collector rules greater than the {str(order)} order.",
            )

        collector_rule_vos = self._get_all_collector_rules(
            target_rule_vo.collector_id,
            target_rule_vo.rule_type,
            target_rule_vo.domain_id,
            target_rule_vo.collector_rule_id,
        )

        collector_rule_vos.insert(order - 1, target_rule_vo)

        i = 0
        for collector_rule_vo in collector_rule_vos:
            if target_rule_vo != collector_rule_vo:
                self.collector_rule_mgr.update_collector_rule_by_vo(
                    {"order": i + 1}, collector_rule_vo
                )
            i += 1

        collector_rule_vo = self.collector_rule_mgr.update_collector_rule_by_vo(
            {"order": order}, target_rule_vo
        )

        return CollectorRuleResponse(**collector_rule_vo.to_dict())

    @transaction(
        permission="inventory-v2:CollectorRule.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def delete(self, params: CollectorRuleDeleteRequest) -> None:
        """Delete collector rule

        Args:
            params (dict): {
                'collector_rule_id': 'str',     # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth (required)
            }

        Returns:
            None
        """

        collector_rule_id = params.collector_rule_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id

        collector_rule_vo = self.collector_rule_mgr.get_collector_rule(
            collector_rule_id, domain_id, workspace_id
        )

        rule_type = collector_rule_vo.rule_type

        if rule_type == "MANAGED":
            raise ERROR_NOT_ALLOWED_TO_DELETE_RULE()

        collector_id = collector_rule_vo.collector_id
        self.collector_rule_mgr.delete_collector_rule_by_vo(collector_rule_vo)

        collector_rule_vos = self._get_all_collector_rules(
            collector_id, rule_type, domain_id
        )

        i = 0
        for collector_rule_vo in collector_rule_vos:
            self.collector_rule_mgr.update_collector_rule_by_vo(
                {"order": i + 1}, collector_rule_vo
            )
            i += 1

    @transaction(
        permission="inventory-v2:CollectorRule.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @convert_model
    def get(
        self, params: CollectorRuleGetRequest
    ) -> Union[CollectorRuleResponse, dict]:
        """Get collector rule

        Args:
            params (dict): {
                'collector_rule_id': 'str',     # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
           CollectorRuleResponse:
        """

        collector_rule_vo = self.collector_rule_mgr.get_collector_rule(
            params.collector_rule_id, params.domain_id, params.workspace_id
        )

        return CollectorRuleResponse(**collector_rule_vo.to_dict())

    @transaction(
        permission="inventory:CollectorRule.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @append_query_filter(
        [
            "collector_rule_id",
            "name",
            "rule_type",
            "collector_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["collector_rule_id", "name"])
    @convert_model
    def list(
        self, params: CollectorRuleSearchQueryRequest
    ) -> Union[CollectorRulesResponse, dict]:
        """List collector rule

        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'collector_rule_id': 'str',
                'name': 'str',
                'rule_type': 'str',
                'collector_id': 'str',
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str',         # injected from auth (required)
            }

        Returns:
            results (list)
            total_count (int)
        """

        query = params.query or {}
        collector_rule_vos, total_count = self.collector_rule_mgr.list_collector_rules(
            query=query
        )

        collector_rule_infos = [
            collector_rule_vo.to_dict() for collector_rule_vo in collector_rule_vos
        ]

        return CollectorRulesResponse(
            results=collector_rule_infos, total_count=total_count
        )

    @transaction(
        permission="inventory:CollectorRule.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["collector_rule_id", "name"])
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @convert_model
    def stat(self, params: CollectorRuleStatQueryRequest) -> dict:
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',     # required
                'domain_id': 'str',     # injected from auth (required)
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.query or {}
        return self.collector_rule_mgr.stat_collector_rules(query)

    def _check_actions(self, actions: dict, domain_id: str) -> None:
        if "change_project" in actions:
            project_id = actions["change_project"]

            identity_mgr: IdentityManager = self.locator.get_manager("IdentityManager")
            identity_mgr.get_project(project_id, domain_id)

        if "match_project" in actions:
            if "source" not in actions["match_project"]:
                raise ERROR_REQUIRED_PARAMETER(key="actions.match_project.source")

        if "match_service_account" in actions:
            if "source" not in actions["match_service_account"]:
                raise ERROR_REQUIRED_PARAMETER(
                    key="actions.match_service_account.source"
                )

    def _get_highest_order(self, collector_id: str, rule_type: str, domain_id: str):
        collector_rule_vos = self.collector_rule_mgr.filter_collector_rules(
            collector_id=collector_id, rule_type=rule_type, domain_id=domain_id
        )

        return collector_rule_vos.count()

    def _get_all_collector_rules(
        self,
        collector_id: str,
        rule_type: str,
        domain_id: str,
        exclude_collector_rule_id: str = None,
    ):
        query = {
            "filter": [
                {"k": "domain_id", "v": domain_id, "o": "eq"},
                {"k": "collector_id", "v": collector_id, "o": "eq"},
                {"k": "rule_type", "v": rule_type, "o": "eq"},
            ],
            "sort": [{"key": "order"}],
        }

        if exclude_collector_rule_id is not None:
            query["filter"].append(
                {"k": "collector_rule_id", "v": exclude_collector_rule_id, "o": "not"}
            )

        collector_rule_vos, total_count = self.collector_rule_mgr.list_collector_rules(
            query
        )
        return list(collector_rule_vos)

    @staticmethod
    def _check_conditions(conditions: list) -> None:
        for condition in conditions:
            key = condition.get("key")
            value = condition.get("value")
            operator = condition.get("operator")

            if not (key and value and operator):
                raise ERROR_INVALID_PARAMETER(
                    key="conditions",
                    reason="Condition should have key, value and operator.",
                )

            if key not in _SUPPORTED_CONDITION_KEYS:
                if not (
                    fnmatch.fnmatch(key, "tags.*") or fnmatch.fnmatch(key, "data.*")
                ):
                    raise ERROR_INVALID_PARAMETER(
                        key="conditions.key",
                        reason=f"Unsupported key. "
                        f'({" | ".join(_SUPPORTED_CONDITION_KEYS)})',
                    )
            if operator not in _SUPPORTED_CONDITION_OPERATORS:
                raise ERROR_INVALID_PARAMETER(
                    key="conditions.operator",
                    reason=f"Unsupported operator. "
                    f'({" | ".join(_SUPPORTED_CONDITION_OPERATORS)})',
                )

    @staticmethod
    def _check_order(order: int) -> None:
        if order <= 0:
            raise ERROR_INVALID_PARAMETER(
                key="order", reason="The order must be greater than 0."
            )
