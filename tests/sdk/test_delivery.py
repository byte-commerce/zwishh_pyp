"""Tests for the DeliveryServiceClient."""
import pytest
import respx
from httpx import Response
import json
import random
from zwishh.sdk.delivery import DeliveryServiceClient

@pytest.fixture
def delivery_client():
    """Fixture for DeliveryServiceClient with mock base URL and API key."""
    return DeliveryServiceClient(
        base_url="http://test-delivery.internal",
        api_key="test-api-key"
    )

@pytest.fixture
def pickup_point():
    return{
        "name": "Pothys silk",
        "phone_number": "9999999999",
        "address": {
            "street_address": "33, Kempegowda Rd, Gandhi Nagar, Bengaluru, Karnataka 560009",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560009",
            "country": "India",
            "latitude": "12.976955130759157",
            "longitude": "77.57907150473682"
        }
    }

@pytest.fixture
def drop_point():
    return{
        "name": "Pai Mobiles",
        "phone_number": "9999999999",
        "address": {
            "street_address": "#14, 80 Feet Road BSK Ist Stage, Srinivasnagar, Bengaluru, Karnataka 560050",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560050",
            "country": "India",
            "latitude": "12.938605659003809",
            "longitude": "77.55581023313424"
        }
    }

@pytest.mark.asyncio
async def test_get_quote(delivery_client, pickup_point, drop_point):
    """Test get_quote method."""
    expected_response = {"quote_id": "quote_123", "amount": 100, "currency": "USD"}
    
    with respx.mock as mock:
        mock.post("http://test-delivery.internal/internal/delivery/get_quote").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await delivery_client.get_quote(
            pickup_address=pickup_point['address'],
            drop_address=drop_point['address'],
            cart_total=1000
        )
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == "/internal/delivery/get_quote"
        assert mock.calls[0].request.method == "POST"

@pytest.mark.asyncio
async def test_place_order(delivery_client, pickup_point, drop_point):
    """Test place_order method."""
    expected_response = {"order_id": 123, "status": "placed"}
    
    with respx.mock as mock:
        mock.post("http://test-delivery.internal/internal/delivery/place_order").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await delivery_client.place_order(
            pickup_point=pickup_point,
            drop_point=drop_point,
            cart_total=1000,
            delivery_partner="shadowfax",
            order_id="zwishh_test_" + str(random.random() * 100000),
            items=[
                {
                    "name": "saree",
                    "quantity": 1,
                    "price": 2500
                }
            ]
        )
        
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
