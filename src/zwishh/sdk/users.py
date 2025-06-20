"""
User Service SDK
=================

Async client for Zwishh User-service. Wraps the HTTP endpoints exposed by
`user-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.users import UserServiceClient

user_client = UserServiceClient(
    base_url="http://user.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

user = await user_client.get_user(123)
print(user["id"])

```
"""
from __future__ import annotations

from .base_client import BaseServiceClient

from typing import Dict, Any

class UserServiceClient(BaseServiceClient):
    """High-level async wrapper for User-service endpoints."""

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user details."""

        endpoint = f"internal/users/{user_id}"
        return await self.get(endpoint)

    async def get_user_address(self, address_id: int) -> Dict[str, Any]:
        """Get user address."""

        endpoint = f"internal/addresses/{address_id}"
        return await self.get(endpoint)

    
        