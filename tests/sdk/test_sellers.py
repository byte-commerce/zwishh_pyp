"""Tests for the SellerServiceClient."""

import pytest
import respx
from httpx import Response

from zwishh.sdk.sellers import SellerServiceClient
from zwishh.sdk.base_client import (
    ServiceClientNotFound,
)


@pytest.fixture
def seller_service() -> SellerServiceClient:
    """Return a SellerServiceClient instance for testing."""
    return SellerServiceClient(base_url="http://test-server", api_key="test-key")


# Test create_seller
@pytest.mark.asyncio
@respx.mock
async def test_create_seller_success(seller_service: SellerServiceClient) -> None:
    """Test successful seller creation."""
    # Arrange
    seller_data = {"phone_number": "+1234567890"}
    expected_seller = {"id": 1, "phone_number": "+1234567890"}
    
    # Mock the HTTP response
    mock_route = respx.post(
        "http://test-server/internal/me",
        json={"phone_number": "+1234567890"},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(201, json=expected_seller))
    
    # Act
    result = await seller_service.create_seller(seller_data)
    
    # Assert
    assert result == expected_seller
    assert mock_route.called


# Test get_seller_by_phone_number
@pytest.mark.asyncio
@respx.mock
async def test_get_seller_by_phone_number_success(seller_service: SellerServiceClient) -> None:
    """Test successful seller retrieval by phone number."""
    # Arrange
    phone_number = "+1234567890"
    expected_seller = {"id": 1, "phone_number": phone_number}
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/phone/{phone_number}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_seller))
    
    # Act
    result = await seller_service.get_seller_by_phone_number(phone_number)
    
    # Assert
    assert result == expected_seller
    assert mock_route.called


# Test get_shop
@pytest.mark.asyncio
@respx.mock
async def test_get_shop_success(seller_service: SellerServiceClient) -> None:
    """Test successful shop retrieval."""
    # Arrange
    shop_id = 123
    expected_shop = {"id": shop_id, "name": "Test Shop"}
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/shops/{shop_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_shop))
    
    # Act
    result = await seller_service.get_shop(shop_id)
    
    # Assert
    assert result == expected_shop
    assert mock_route.called


# Test get_product_variant_details
@pytest.mark.asyncio
@respx.mock
async def test_get_product_variant_details_success(seller_service: SellerServiceClient) -> None:
    """Test successful product variant details retrieval."""
    # Arrange
    product_id = "prod_123"
    variant_id = "var_456"
    expected_variant = {"id": variant_id, "product_id": product_id, "price": 999}
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/products/{product_id}/variants/{variant_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_variant))
    
    # Act
    result = await seller_service.get_product_variant_details(product_id, variant_id)
    
    # Assert
    assert result == expected_variant
    assert mock_route.called


# Test error handling
@pytest.mark.asyncio
@respx.mock
async def test_get_shop_not_found(seller_service: SellerServiceClient) -> None:
    """Test shop not found scenario."""
    # Arrange
    shop_id = 999
    
    # Mock 404 response
    respx.get(
        f"http://test-server/internal/shops/{shop_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, text="Shop not found"))
    
    # Act & Assert
    with pytest.raises(ServiceClientNotFound):
        await seller_service.get_shop(shop_id)


# Test API key injection
@pytest.mark.asyncio
@respx.mock
async def test_api_key_injection(seller_service: SellerServiceClient) -> None:
    """Test that the API key is properly injected into requests."""
    # Arrange
    phone_number = "+1234567890"
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/phone/{phone_number}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json={"id": 1, "phone_number": phone_number}))
    
    # Act
    await seller_service.get_seller_by_phone_number(phone_number)
    
    # Assert
    assert mock_route.called
    assert mock_route.calls[0].request.headers["x-service-api-key"] == "test-key"
