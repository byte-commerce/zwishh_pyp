from redis.asyncio import Redis
import time


class FakeRedis:
    """Small in-memory fallback so the service can still boot without Redis."""

    def __init__(self):
        self.store: dict[str, int] = {}
        self.expiry: dict[str, float] = {}

    async def ping(self):
        return True

    def _cleanup(self, key: str):
        expiry = self.expiry.get(key)

        if expiry and time.time() > expiry:
            self.store.pop(key, None)
            self.expiry.pop(key, None)

    async def incr(self, key: str) -> int:
        self._cleanup(key)

        value = self.store.get(key, 0) + 1
        self.store[key] = value

        return value

    async def expire(self, key: str, seconds: int):
        self.expiry[key] = time.time() + seconds
        return True


redis_client: Redis | FakeRedis | None = None


async def get_redis(
    useRedis: bool,
    host: str,
    port: int,
    db: int,
    password: str,
) -> Redis | FakeRedis:
    """
    Returns a singleton Redis client.

    Falls back to FakeRedis if:
    - Redis is disabled
    - Redis connection fails
    """

    global redis_client

    if redis_client is not None:
        return redis_client

    if not useRedis:
        redis_client = FakeRedis()
        return redis_client

    try:
        redis_client = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )

        await redis_client.ping()

    except Exception:
        redis_client = FakeRedis()

    return redis_client