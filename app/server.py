import grpc
from concurrent import futures
import ipaddress
import subprocess
import asyncio
import os
from grpc_dir import ping_pb2, ping_pb2_grpc

# health
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_health.v1 import health as health_srv

GRPC_PORT = int(os.getenv("GRPC_PORT", 50151))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 10))



class PingService(ping_pb2_grpc.PingServiceServicer):
    async def _ping_one(self, target):
        try:
            proc = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "1", target,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            await proc.wait()
            return target, (proc.returncode == 0)
        except Exception:
            return target, False

    async def CheckIPs(self, request, context):
        tasks = []
        expanded = []
        for item in request.ip_list:
            try:
                net = ipaddress.ip_network(item, strict=False)
                expanded.extend(str(ip) for ip in net.hosts())
            except ValueError:
                expanded.append(item)

        for ip in expanded:
            tasks.append(self._ping_one(ip))
        results = await asyncio.gather(*tasks)
        print(results)
        return ping_pb2.PingResponse(
            results=[ping_pb2.PingResult(target=t, reachable=r) for t, r in results]
        )

async def serve():
    # non-async health server implementation provided by grpcio-health-checking
    health_manager = health_srv.HealthServicer()
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))

    # register services
    ping_pb2_grpc.add_PingServiceServicer_to_server(PingService(), server)
    health_pb2_grpc.add_HealthServicer_to_server(health_manager, server)

    # set overall serving status to NOT_SERVING until ready
    health_manager.set('', health_pb2.HealthCheckResponse.NOT_SERVING)

    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    await server.start()
    # once server started, mark as SERVING
    health_manager.set('', health_pb2.HealthCheckResponse.SERVING)
    print(f"PingService running on port {GRPC_PORT}")

    try:
        await server.wait_for_termination()
    finally:
        # on shutdown mark NOT_SERVING
        health_manager.set('', health_pb2.HealthCheckResponse.NOT_SERVING)
        await server.stop(5)

if __name__ == "__main__":
    asyncio.run(serve())