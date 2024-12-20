from spaceone.api.inventory_v2.v1 import collector_rule_pb2, collector_rule_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.inventory_v2.service.collector_rule_service import CollectorRuleService


class CollectorRule(BaseAPI, collector_rule_pb2_grpc.CollectorRuleServicer):
    pb2 = collector_rule_pb2
    pb2_grpc = collector_rule_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        response: dict = collector_rule_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        response: dict = collector_rule_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        collector_rule_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        response: dict = collector_rule_svc.get(params)
        return self.dict_to_message(response)

    def change_order(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        response: dict = collector_rule_svc.change_order(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        response: dict = collector_rule_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        collector_rule_svc = CollectorRuleService(metadata)
        response: dict = collector_rule_svc.stat(params)
        return self.dict_to_message(response)
