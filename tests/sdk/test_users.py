"""Tests for the UserServiceClient."""

import pytest
import respx
from httpx import Response

from zwishh.sdk.users import UserServiceClient
from zwishh.sdk.base_client import (
    ServiceClientNotFound,
    ServiceClientUnauthorized,
)


@pytest.fixture
def user_service() -> UserServiceClient:
    """Return a UserServiceClient instance for testing."""
    return UserServiceClient(base_url="http://test-server", api_key="test-key")


# Test get_user
@pytest.mark.asyncio
@respx.mock
async def test_get_user_success(user_service: UserServiceClient) -> None:
    """Test successful user retrieval."""
    # Arrange
    user_id = 123
    expected_user = {"id": user_id, "name": "Test User", "email": "test@example.com"}
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/users/{user_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_user))
    
    # Act
    user = await user_service.get_user(user_id)
    
    # Assert
    assert user == expected_user
    assert mock_route.called


# Test get_user_address
@pytest.mark.asyncio
@respx.mock
async def test_get_user_address_success(user_service: UserServiceClient) -> None:
    """Test successful user address retrieval."""
    # Arrange
    user_id = 123
    address_id = 456
    expected_address = {
        "id": address_id, 
        "user_id": user_id,
        "street": "123 Test St",
        "city": "Test City"
    }
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/users/{user_id}/addresses/{address_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json=expected_address))
    
    # Act
    address = await user_service.get_user_address(user_id, address_id)
    
    # Assert
    assert address == expected_address
    assert mock_route.called


# Test error handling - User not found
@pytest.mark.asyncio
@respx.mock
async def test_get_user_not_found(user_service: UserServiceClient) -> None:
    """Test user not found scenario."""
    # Arrange
    user_id = 999
    
    # Mock 404 response
    respx.get(
        f"http://test-server/internal/users/{user_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, text="User not found"))
    
    # Act & Assert
    with pytest.raises(ServiceClientNotFound):
        await user_service.get_user(user_id)


# Test error handling - Unauthorized
@pytest.mark.asyncio
@respx.mock
async def test_get_user_unauthorized(user_service: UserServiceClient) -> None:
    """Test unauthorized access to user data."""
    # Arrange
    user_id = 123
    
    # Mock 401 response
    respx.get(
        f"http://test-server/internal/users/{user_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(401, text="Unauthorized"))
    
    # Act & Assert
    with pytest.raises(ServiceClientUnauthorized):
        await user_service.get_user(user_id)


# Test error handling - Address not found
@pytest.mark.asyncio
@respx.mock
async def test_get_user_address_not_found(user_service: UserServiceClient) -> None:
    """Test address not found scenario."""
    # Arrange
    user_id = 123
    address_id = 999
    
    # Mock 404 response
    respx.get(
        f"http://test-server/internal/users/{user_id}/addresses/{address_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(404, text="Address not found"))
    
    # Act & Assert
    with pytest.raises(ServiceClientNotFound):
        await user_service.get_user_address(user_id, address_id)


# Test API key injection
@pytest.mark.asyncio
@respx.mock
async def test_api_key_injection(user_service: UserServiceClient) -> None:
    """Test that the API key is properly injected into requests."""
    # Arrange
    user_id = 123
    
    # Mock the HTTP response
    mock_route = respx.get(
        f"http://test-server/internal/users/{user_id}",
        headers={"X-Service-API-Key": "test-key"}
    ).mock(return_value=Response(200, json={"id": user_id, "name": "Test User"}))
    
    # Act
    await user_service.get_user(user_id)
    
    # Assert
    assert mock_route.called
    assert mock_route.calls[0].request.headers["x-service-api-key"] == "test-key"
