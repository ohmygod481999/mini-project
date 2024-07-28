import asyncio
import time
from typing import Optional
import redis.asyncio as redis
from redis.asyncio.client import Pipeline


class ConcurrencyControl:
    def __init__(
        self,
        max_connections: int,
        max_connection_per_client: int,
        redis_key: Optional[str] = None,
    ) -> None:
        self.redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.redis_key = redis_key if redis_key else "concurrency_control"
        self.max_connections = max_connections
        self.max_connections_per_client = max_connection_per_client

    async def _get_hash_map(self, pipe: Optional[Pipeline] = None) -> dict:
        client = pipe if pipe else self.redis_client
        hash_map = await client.hgetall(self.redis_key)
        return {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in hash_map.items()
        }

    async def _increase_connection(self, client_id: str, pipe: Pipeline) -> None:
        await pipe.hincrby(self.redis_key, client_id, 1)

    async def _decrease_connection(self, client_id: str) -> None:
        await self.redis_client.hincrby(self.redis_key, client_id, -1)

    def can_client_connect(self, hash_map: dict, client_id: str) -> bool:
        total_connections = sum(int(value) for value in hash_map.values())
        if total_connections >= self.max_connections:
            return False

        if client_id not in hash_map:
            return True

        if int(hash_map[client_id]) >= self.max_connections_per_client:
            return False

        return True

    async def acquire_connection(self, client_id: str) -> bool:
        # redis lua script
        lua_script = """
        local key = KEYS[1]
        local client_id = ARGV[1]
        local max_connections = tonumber(ARGV[2])
        local max_connection_per_client = tonumber(ARGV[3])

        local hash_map = redis.call('HGETALL', key)
        local total_connections = 0
        local client_connections = 0

        for i = 1, #hash_map, 2 do
            total_connections = total_connections + tonumber(hash_map[i + 1])
            if hash_map[i] == client_id then
                client_connections = tonumber(hash_map[i + 1])
            end
        end

        if total_connections >= max_connections then
            return 0
        end

        if client_connections >= max_connection_per_client then
            return 0
        end

        redis.call('HINCRBY', key, client_id, 1)
        return 1
        """
        # print("client_id", client_id)
        # print("max_connections", self.max_connections)
        # print("max_connection_per_client", self.max_connections_per_client)
        acquire = self.redis_client.register_script(lua_script)
        ok = await acquire(
            keys=[self.redis_key],
            args=[client_id, self.max_connections, self.max_connections_per_client],
        )
        return bool(ok)

    async def release_connection(self, client_id: str) -> None:
        print(f"[Client {client_id}] released connection")
        await self._decrease_connection(client_id)

    async def clean_all_sessions(self) -> None:
        await self.redis_client.delete(self.redis_key)
