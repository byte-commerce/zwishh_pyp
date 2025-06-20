"""
Seller Service SDK
=================

Async client for Zwishh Seller-service. Wraps the HTTP endpoints exposed by
`seller-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.sellers import SellerServiceClient

seller_client = SellerServiceClient(
    base_url="http://seller.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

seller = await seller_client.create_seller(seller)
print(seller["id"])

```
"""
from __future__ import annotations

from .base_client import BaseServiceClient

from typing import Dict, Any

class SellerServiceClient(BaseServiceClient):
    """High-level async wrapper for Seller-service endpoints."""

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    async def create_seller(
        self,
        seller: dict,
    ) -> Dict[str, Any]:
        """Create a seller."""

        endpoint = "me"
        data = {
            "phone_number": seller["phone_number"],
        }
        return await self.post(endpoint, json=data)

    async def get_seller_by_phone_number(
        self,
        phone_number: str,
    ) -> Dict[str, Any]:
        """Get seller by phone number."""

        endpoint = f"phone/{phone_number}"
        return await self.get(endpoint)

    async def get_shop(self, shop_id: int) -> Dict[str, Any]:
        """Get shop details."""

        endpoint = f"internal/shops/{shop_id}"
        return await self.get(endpoint)

    async def get_product_variant_details(
        self, 
        product_id: str, 
        variant_id: str, 
    ) -> Dict[str, Any]:
        """Fetch variant details from seller service."""

        endpoint = f"internal/products/{product_id}/variants/{variant_id}"
        return await self.get(endpoint)
