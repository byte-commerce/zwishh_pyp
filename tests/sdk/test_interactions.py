"""Tests for the InteractionServiceClient."""

import pytest
import respx
from httpx import Response

from zwishh.sdk.interactions import InteractionServiceClient
from zwishh.sdk.base_client import (
    NonRetryableHTTPError,
)


@pytest.fixture
def interaction_service() -> InteractionServiceClient:
    """Return an InteractionServiceClient instance for testing."""
    return InteractionServiceClient(
        base_url="http://test-server", 
        api_key="test-key"
    )


@pytest.mark.asyncio
@respx.mock
async def test_get_followers_count_success(interaction_service: InteractionServiceClient) -> None:
    """Test successful retrieval of followers count."""
    # Arrange
    seller_id = 123
    expected_count = {"count": 42}
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/sellers/{seller_id}/followers/count",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_count))
    
    # Act
    result = await interaction_service.get_followers_count(seller_id)
    
    # Assert
    assert result == expected_count
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_get_followers_count_not_found(interaction_service: InteractionServiceClient) -> None:
    """Test followers count for non-existent seller."""
    # Arrange
    seller_id = 999
    
    # Mock 404 response
    respx.get(
        f"http://test-server/sellers/{seller_id}/followers/count",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, json={"detail": "Seller not found"}))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await interaction_service.get_followers_count(seller_id)


@pytest.mark.asyncio
@respx.mock
async def test_get_likes_count_success(interaction_service: InteractionServiceClient) -> None:
    """Test successful retrieval of likes count for products."""
    # Arrange
    product_ids = [1, 2, 3]
    expected_response = {
        "counts": [
            {"product_id": 1, "likes": 5},
            {"product_id": 2, "likes": 3},
            {"product_id": 3, "likes": 7}
        ]
    }
    
    # Mock the HTTP response
    mock_route = respx.get(
        "http://test-server/products/likes/count",
        params={"product_ids": [1, 2, 3]},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_response))
    
    # Act
    result = await interaction_service.get_likes_count(product_ids)
    
    # Assert
    assert result == expected_response
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_get_views_count_success(interaction_service: InteractionServiceClient) -> None:
    """Test successful retrieval of view counts for products."""
    # Arrange
    product_ids = [1, 2, 3]
    expected_response = {
        "views": [
            {"product_id": 1, "views": 150},
            {"product_id": 2, "views": 230},
            {"product_id": 3, "views": 75}
        ]
    }
    
    # Mock the HTTP response
    mock_route = respx.get(
        "http://test-server/products/view-totals",
        params={"product_ids": [1, 2, 3]},
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_response))
    
    # Act
    result = await interaction_service.get_views_count(product_ids)
    
    # Assert
    assert result == expected_response
    assert mock_route.called


@pytest.mark.asyncio
@respx.mock
async def test_api_key_injection(interaction_service: InteractionServiceClient) -> None:
    """Test that the API key is properly injected into requests."""
    # Arrange
    seller_id = 123
    expected_count = {"count": 42}
    
    # Mock the HTTP response with API key validation
    mock_route = respx.get(
        f"http://test-server/sellers/{seller_id}/followers/count",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_count))
    
    # Act
    await interaction_service.get_followers_count(seller_id)
    
    # Assert
    assert mock_route.called
    assert mock_route.calls[0].request.headers["X-Service-API-Key"] == "test-key"


@pytest.mark.asyncio
@respx.mock
async def test_unauthorized_access(interaction_service: InteractionServiceClient) -> None:
    """Test unauthorized access to the API."""
    # Arrange
    seller_id = 123
    
    # Mock 401 response
    respx.get(
        f"http://test-server/sellers/{seller_id}/followers/count",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(401, json={"detail": "Unauthorized"}))
    
    # Act & Assert
    with pytest.raises(NonRetryableHTTPError):
        await interaction_service.get_followers_count(seller_id)
