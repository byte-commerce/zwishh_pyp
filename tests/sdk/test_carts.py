"""Tests for the CartServiceClient."""

import pytest
import respx
from httpx import Response

from zwishh.sdk.carts import CartServiceClient
from zwishh.sdk.base_client import (
    NonRetryableHTTPError,
)


@pytest.fixture
def cart_service() -> CartServiceClient:
    """Return a CartServiceClient instance for testing."""
    return CartServiceClient(base_url="http://test-server", api_key="test-key")


@pytest.mark.asyncio
@respx.mock
async def test_get_cart_success(cart_service: CartServiceClient) -> None:
    """Test successful cart retrieval."""
    # Arrange
    cart_id = 123
    expected_cart = {"id": cart_id, "items": [{"product_id": 1, "quantity": 2}], "items_total": 2}
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/carts/{cart_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_cart))
    
    # Act
    cart = await cart_service.get_cart(cart_id)
    
    # Assert
    assert cart == expected_cart
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_get_cart_not_found(cart_service: CartServiceClient) -> None:
    """Test cart not found scenario."""
    # Arrange
    cart_id = 999
    
    # Mock 404 response
    respx.get(
        f"http://test-server/internal/carts/{cart_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, text="Cart not found"))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await cart_service.get_cart(cart_id)


@pytest.mark.asyncio
@respx.mock
async def test_get_cart_unauthorized(cart_service: CartServiceClient) -> None:
    """Test unauthorized access scenario."""
    # Arrange
    cart_id = 123
    
    # Mock 401 response
    respx.get(
        f"http://test-server/internal/carts/{cart_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(401, text="Unauthorized"))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await cart_service.get_cart(cart_id)


@pytest.mark.asyncio
@respx.mock
async def test_delete_cart_success(cart_service: CartServiceClient) -> None:
    """Test successful cart deletion."""
    # Arrange
    cart_id = 123
    
    # Mock the HTTP response
    mock_route = respx.delete(
        f"http://test-server/internal/carts/{cart_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json={"status": "deleted"}))
    
    # Act
    result = await cart_service.delete_cart(cart_id)
    
    # Assert
    assert result == {"status": "deleted"}
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_delete_cart_not_found(cart_service: CartServiceClient) -> None:
    """Test cart not found during deletion."""
    # Arrange
    cart_id = 999
    
    # Mock 404 response
    respx.delete(
        f"http://test-server/internal/carts/{cart_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, text="Cart not found"))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await cart_service.delete_cart(cart_id)



@pytest.mark.asyncio
@respx.mock
async def test_unlock_cart_success(cart_service: CartServiceClient) -> None:
    """Test successful cart unlock."""
    # Arrange
    cart_id = 123
    
    # Mock the HTTP response
    mock_route = respx.patch(
        f"http://test-server/internal/carts/{cart_id}/unlock",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json={"status": "unlocked"}))
    
    # Act
    result = await cart_service.unlock_cart(cart_id)
    
    # Assert
    assert result == {"status": "unlocked"}
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_unlock_cart_not_found(cart_service: CartServiceClient) -> None:
    """Test cart not found during unlock."""
    # Arrange
    cart_id = 999
    
    # Mock 404 response
    respx.patch(
        f"http://test-server/internal/carts/{cart_id}/unlock",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, text="Cart not found"))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await cart_service.unlock_cart(cart_id)



@pytest.mark.asyncio
@respx.mock
async def test_api_key_injection(cart_service: CartServiceClient) -> None:
    """Test that the API key is properly injected into requests."""
    # Arrange
    cart_id = 123
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/carts/{cart_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json={"id": cart_id}))
    
    # Act
    await cart_service.get_cart(cart_id)
    
    # Assert
    assert mock_route.called
    assert mock_route.calls[0].request.headers["x-service-api-key"] == "test-key"
