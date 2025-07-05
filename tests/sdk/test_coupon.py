"""Tests for the CouponServiceClient."""
import pytest
import respx
from httpx import Response
from zwishh.sdk.coupon import CouponServiceClient
from zwishh.sdk.base_client import ServiceClientNotFound


@pytest.fixture
def coupon_client():
    """Fixture for CouponServiceClient with mock base URL and API key."""
    return CouponServiceClient(
        base_url="http://test-coupon.internal",
        api_key="test-api-key"
    )

@pytest.mark.asyncio
async def test_get_coupon(coupon_client):
    """Test get_coupon method."""
    coupon_code = "SUMMER25"
    expected_response = {
        "code": coupon_code,
        "discount": 25,
        "type": "percentage",
        "valid": True
    }
    
    with respx.mock as mock:
        mock.get(f"http://test-coupon.internal/internal/coupon/{coupon_code}").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await coupon_client.get_coupon(coupon_code)
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == f"/internal/coupon/{coupon_code}"
        assert mock.calls[0].request.method == "GET"

@pytest.mark.asyncio
async def test_apply_coupon(coupon_client):
    """Test apply_coupon method."""
    coupon_code = "SUMMER25"
    expected_response = {
        "applied": True,
        "discount_applied": 25.0,
        "message": "Coupon applied successfully"
    }
    
    with respx.mock as mock:
        mock.post("http://test-coupon.internal/internal/coupon/apply").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await coupon_client.apply_coupon(coupon_code)
        
        assert response == expected_response
        assert mock.calls[0].request.url.path == "/internal/coupon/apply"
        assert mock.calls[0].request.method == "POST"

@pytest.mark.asyncio
async def test_invalid_coupon(coupon_client):
    """Test behavior with invalid coupon code."""
    invalid_coupon = "INVALID123"
    error_response = {
        "error": "Coupon not found",
        "status_code": 404
    }
    
    with respx.mock as mock:
        mock.get(f"http://test-coupon.internal/internal/coupon/{invalid_coupon}").mock(
            return_value=Response(404, json=error_response)
        )
        
        with pytest.raises(ServiceClientNotFound):
            response = await coupon_client.get_coupon(invalid_coupon)
        
            assert response == error_response
            assert mock.calls[0].request.url.path == f"/internal/coupon/{invalid_coupon}"
            assert mock.calls[0].request.method == "GET"
