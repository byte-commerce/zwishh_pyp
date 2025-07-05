"""Tests for the DeliveryServiceClient."""
import pytest
import respx
from httpx import Response
import json
from zwishh.sdk.delivery import DeliveryServiceClient

@pytest.fixture
def delivery_client():
    """Fixture for DeliveryServiceClient with mock base URL and API key."""
    return DeliveryServiceClient(
        base_url="http://test-delivery.internal",
        api_key="test-api-key"
    )

@pytest.mark.asyncio
async def test_get_quote(delivery_client):
    """Test get_quote method."""
    test_order = {"order_id": 123, "items": [{"id": 1, "quantity": 2}]}
    expected_response = {"quote_id": "quote_123", "amount": 100, "currency": "USD"}
    
    with respx.mock as mock:
        mock.post("http://test-delivery.internal/internal/delivery/get_quote").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await delivery_client.get_quote(test_order)
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == "/internal/delivery/get_quote"
        assert mock.calls[0].request.method == "POST"

@pytest.mark.asyncio
async def test_place_order(delivery_client):
    """Test place_order method."""
    test_order = {"order_id": 123, "items": [{"id": 1, "quantity": 2}]}
    expected_response = {"order_id": 123, "status": "placed"}
    
    with respx.mock as mock:
        mock.post("http://test-delivery.internal/internal/delivery/place_order").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await delivery_client.place_order(test_order)
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == "/internal/delivery/place_order"
        assert mock.calls[0].request.method == "POST"

@pytest.mark.asyncio
async def test_cancel_order(delivery_client):
    """Test cancel_order method."""
    order_id = 123
    expected_response = {"order_id": order_id, "status": "cancelled"}
    
    with respx.mock as mock:
        mock.post("http://test-delivery.internal/internal/delivery/cancel_order").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await delivery_client.cancel_order(order_id)
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == "/internal/delivery/cancel_order"
        assert mock.calls[0].request.method == "POST"

@pytest.mark.asyncio
async def test_track_order(delivery_client):
    """Test track_order method."""
    order_id = 123
    expected_response = {"order_id": order_id, "status": "in_transit", "location": "WAREHOUSE"}
    
    with respx.mock as mock:
        mock.post("http://test-delivery.internal/internal/delivery/track_order").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await delivery_client.track_order(order_id)
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == "/internal/delivery/track_order"
        assert mock.calls[0].request.method == "POST"
