from spaceone.api.inventory_v2.v1 import region_pb2, region_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.inventory_v2.service.region_service import RegionService


class Region(BaseAPI, region_pb2_grpc.RegionServicer):
    pb2 = region_pb2
    pb2_grpc = region_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        region_svc = RegionService(metadata)
        response: dict = region_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        region_svc = RegionService(metadata)
        response: dict = region_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        region_svc = RegionService(metadata)
        region_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        region_svc = RegionService(metadata)
        response: dict = region_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        region_svc = RegionService(metadata)
        response: dict = region_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        region_svc = RegionService(metadata)
        response: dict = region_svc.stat(params)
        return self.dict_to_message(response)
