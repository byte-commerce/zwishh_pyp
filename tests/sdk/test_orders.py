"""Tests for the OrderServiceClient."""

import pytest
import respx
from httpx import Response

from zwishh.sdk.orders import OrderServiceClient
from zwishh.sdk.base_client import (
    NonRetryableHTTPError,
)


@pytest.fixture
def order_service() -> OrderServiceClient:
    """Return an OrderServiceClient instance for testing."""
    return OrderServiceClient(base_url="http://test-server", api_key="test-key")


@pytest.mark.asyncio
@respx.mock
async def test_create_order_success(order_service: OrderServiceClient) -> None:
    """Test successful order creation."""
    # Arrange
    cart_data = {"id": 123, "items": [{"product_id": 1, "quantity": 2}]}
    expected_order = {"id": 456, "cart_id": 123, "status": "created"}
    
    # Mock the HTTP response
    mock_route = respx.post(
        "http://test-server/internal/orders",
        json={"cart": cart_data},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(201, json=expected_order))
    
    # Act
    order = await order_service.create_order(cart_data)
    
    # Assert
    assert order == expected_order
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_create_order_unauthorized(order_service: OrderServiceClient) -> None:
    """Test unauthorized order creation."""
    # Arrange
    cart_data = {"id": 123, "items": [{"product_id": 1, "quantity": 2}]}
    
    # Mock 401 response
    respx.post(
        "http://test-server/internal/orders",
        json={"cart": cart_data},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(401, text="Unauthorized"))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await order_service.create_order(cart_data)


@pytest.mark.asyncio
@respx.mock
async def test_create_order_validation_error(order_service: OrderServiceClient) -> None:
    """Test order creation with invalid data."""
    # Arrange
    invalid_cart = {"id": 123}  # Missing required items
    
    # Mock 400 response
    respx.post(
        "http://test-server/internal/orders",
        json={"cart": invalid_cart},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(400, json={"detail": "Missing required field: items"}))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await order_service.create_order(invalid_cart)


@pytest.mark.asyncio
@respx.mock
async def test_api_key_injection(order_service: OrderServiceClient) -> None:
    """Test that the API key is properly injected into requests."""
    # Arrange
    cart_data = {"id": 123, "items": [{"product_id": 1, "quantity": 2}]}
    
    # Mock the HTTP response
    mock_route = respx.post(
        "http://test-server/internal/orders",
        json={"cart": cart_data},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(201, json={"id": 456}))
    
    # Act
    await order_service.create_order(cart_data)
    
    # Assert
    assert mock_route.called
    assert mock_route.calls[0].request.headers["x-service-api-key"] == "test-key"
