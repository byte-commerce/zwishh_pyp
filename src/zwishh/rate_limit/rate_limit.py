import inspect
import logging
import time
import uuid
from hashlib import sha256

from fastapi import Depends, HTTPException, Request

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host if request.client else uuid.uuid4().hex


def normalize_query(query: str) -> str:
    return " ".join(query.lower().split())


def _hash_value(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:16]


async def _enforce_rate_limit(
    identifier: str,
    api_name: str,
    limit_per_sec: int,
    redis_client,
):
    if not identifier:
        raise HTTPException(
            status_code=400,
            detail="Missing rate limit identifier",
        )

    current_time = time.time()
    current_second = int(current_time)

    safe_identifier = _hash_value(identifier)

    key = f"rl:{api_name}:{safe_identifier}:{current_second}"

    count = await redis_client.incr(key)

    if count == 1:
        ttl = 1 - (current_time - current_second)
        await redis_client.expire(key, int(ttl) + 1)

    if count > limit_per_sec:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {api_name}. Try again next second.",
            headers={
                "Retry-After": "1",
            },
        )


def rate_limit_dependency(
    api_name: str,
    identifier_func,
    limit_per_sec: int,
    redis_dependency,
):
    """
    Creates a FastAPI dependency for rate limiting.

    Parameters:
        api_name: Name of the API being protected.
        identifier_func: Function that extracts the identifier from the request.
                         Can be either sync or async.
        limit_per_sec: Allowed requests per second.
        redis_dependency: FastAPI dependency that returns a Redis client.
    """

    async def dependency(
        request: Request,
        redis_client=Depends(redis_dependency),
    ):
        identifier = identifier_func(request)

        # Support both sync and async identifier functions
        if inspect.isawaitable(identifier):
            identifier = await identifier

        await _enforce_rate_limit(
            identifier=identifier,
            api_name=api_name,
            limit_per_sec=limit_per_sec,
            redis_client=redis_client,
        )

    return dependency