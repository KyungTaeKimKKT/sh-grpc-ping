import grpc
import os
import asyncio
import time

from grpc_dir import ping_pb2, ping_pb2_grpc
# health
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_health.v1 import health as health_srv

GRPC_PORT = int(os.getenv("GRPC_PORT", 50151))
HOST = os.getenv("HOST", "localhost")
CHANNEL = f"{HOST}:{GRPC_PORT}"
IP_LIST = os.getenv("IP_LIST", "8.8.8.8,192.168.7.0/24,redis.host.sh").split(",")


### k3s로  grpc가 배포된 이후 테스트 코드임
# async def main():
#     target = "ping.grpc.sh:5555"
#     # target = "localhost:50051"
#     print(f"Connecting to {target} ...")
#     async with grpc.aio.insecure_channel(target) as channel:
#         stub = ping_pb2_grpc.PingServiceStub(channel)
#         req = ping_pb2.PingRequest(ip_list=["8.8.8.8"])
#         try:
#             resp = await stub.CheckIPs(req, timeout=5)
#             for r in resp.results:
#                 print(f"{r.target}: {'OK' if r.reachable else 'FAIL'}")
#         except grpc.aio.AioRpcError as e:
#             print(f"RPC failed: {e.code().name} - {e.details()}")

def grpc_health_check(target:str, timeout:int=2) -> bool:
  try:
      with grpc.insecure_channel(target) as ch:
          stub = health_pb2_grpc.HealthStub(ch)
          req = health_pb2.HealthCheckRequest(service="")
          resp = stub.Check(req, timeout=timeout)
          return resp.status == health_pb2.HealthCheckResponse.SERVING
  except Exception as e:
      print(f"[grpc_health_check] {e}")
      return False

# def main():
#     # target = "ping.grpc.sh:5555"
#     target = "localhost:50151"
#     print(f"Connecting to {target} ...")
#     async with grpc.aio.insecure_channel(target) as channel:
#         stub = ping_pb2_grpc.PingServiceStub(channel)
#         req = ping_pb2.PingRequest(ip_list=["8.8.8.8"])
#         try:
#             resp = await stub.CheckIPs(req, timeout=5)
#             for r in resp.results:
#                 print(f"{r.target}: {'OK' if r.reachable else 'FAIL'}")
#         except grpc.aio.AioRpcError as e:
#             print(f"RPC failed: {e.code().name} - {e.details()}")

if __name__ == "__main__":
    target = "localhost:50151"
    print( "grpc_health_check: ", target, ':', grpc_health_check(target = target))


#### 동기식 plain 코드임(no image화)
# def run():
#     with grpc.insecure_channel(CHANNEL) as channel:
#         stub = ping_pb2_grpc.PingServiceStub(channel)
#         req = ping_pb2.PingRequest(ip_list=IP_LIST)

#         s = time.perf_counter()
#         resp = stub.CheckIPs(req)
#         e = time.perf_counter()

#         for r in resp.results:
#             print(f"{r.target}: {'OK' if r.reachable else 'FAIL'}")

#         print(f"Time taken: {int((e-s)*1000)} msec")

# if __name__ == "__main__":
#     run()

#### 비동기식 plain 코드임(no image화)
# async def run():
#     async with grpc.aio.insecure_channel(CHANNEL) as channel:
#         stub = ping_pb2_grpc.PingServiceStub(channel)
#         req = ping_pb2.PingRequest(ip_list=IP_LIST)

#         s = time.perf_counter()
#         resp = await stub.CheckIPs(req)
#         e = time.perf_counter()

#         for r in resp.results:
#             print(f"{r.target}: {'OK' if r.reachable else 'FAIL'}")
#         print(f"Time taken: {int((e-s)*1000)} msec")
# if __name__ == "__main__":
#     asyncio.run(run())