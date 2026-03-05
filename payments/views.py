"""
Payment views for eSewa and Khalti (Nepal payment gateways).
"""
import base64
import hashlib
import hmac
import uuid

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# --- eSewa ---

def _esewa_signature(total_amount: str, transaction_uuid: str, product_code: str) -> str:
    """Generate HMAC-SHA256 signature for eSewa."""
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    secret = settings.ESEWA_SECRET_KEY
    sig = hmac.new(
        secret.encode() if isinstance(secret, str) else secret,
        message.encode(),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(sig).decode()


@api_view(['POST'])
@permission_classes([AllowAny])
def esewa_initiate(request):
    """
    Initiate eSewa payment. Returns form data for redirect.
    Body: {
        "amount": 100,           # product amount (NPR)
        "tax_amount": 10,        # optional, default 0
        "product_name": "...",   # optional
        "success_url": "...",   # required
        "failure_url": "..."    # required
    }
    """
    data = request.data
    amount = float(data.get('amount', 0))
    tax_amount = float(data.get('tax_amount', 0))
    service_charge = float(data.get('product_service_charge', 0))
    delivery_charge = float(data.get('product_delivery_charge', 0))
    success_url = data.get('success_url', '')
    failure_url = data.get('failure_url', '')

    if amount <= 0:
        return Response(
            {'error': 'amount is required and must be greater than 0'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not success_url or not failure_url:
        return Response(
            {'error': 'success_url and failure_url are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    total_amount = amount + tax_amount + service_charge + delivery_charge
    transaction_uuid = str(uuid.uuid4()).replace('-', '')[:20]
    product_code = settings.ESEWA_PRODUCT_CODE

    signature = _esewa_signature(
        str(int(total_amount)),
        transaction_uuid,
        product_code,
    )

    form_url = (
        'https://epay.esewa.com.np/api/epay/main/v2/form'
        if settings.ESEWA_USE_PRODUCTION
        else 'https://rc-epay.esewa.com.np/api/epay/main/v2/form'
    )

    return Response({
        'form_url': form_url,
        'form_data': {
            'amount': str(int(amount)),
            'tax_amount': str(int(tax_amount)),
            'total_amount': str(int(total_amount)),
            'transaction_uuid': transaction_uuid,
            'product_code': product_code,
            'product_service_charge': str(int(service_charge)),
            'product_delivery_charge': str(int(delivery_charge)),
            'success_url': success_url,
            'failure_url': failure_url,
            'signed_field_names': 'total_amount,transaction_uuid,product_code',
            'signature': signature,
        },
        'transaction_uuid': transaction_uuid,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def esewa_verify(request):
    """
    Verify eSewa transaction status.
    Query params: product_code, total_amount, transaction_uuid
    """
    product_code = request.query_params.get('product_code', settings.ESEWA_PRODUCT_CODE)
    total_amount = request.query_params.get('total_amount', '')
    transaction_uuid = request.query_params.get('transaction_uuid', '')

    if not total_amount or not transaction_uuid:
        return Response(
            {'error': 'total_amount and transaction_uuid are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    base_url = (
        'https://epay.esewa.com.np'
        if settings.ESEWA_USE_PRODUCTION
        else 'https://uat.esewa.com.np'
    )
    url = f"{base_url}/api/epay/transaction/status/"
    params = {
        'product_code': product_code,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return Response(data)
    except requests.RequestException as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )


# --- Khalti ---

def _khalti_base_url():
    return 'https://khalti.com/api/v2' if settings.KHALTI_USE_PRODUCTION else 'https://dev.khalti.com/api/v2'


@api_view(['POST'])
@permission_classes([AllowAny])
def khalti_initiate(request):
    """
    Initiate Khalti payment. Returns payment_url to redirect user.
    Body: {
        "amount": 1000,         # in paisa (min 1000 = Rs 10)
        "purchase_order_id": "order-123",
        "purchase_order_name": "Product Name",
        "return_url": "...",
        "website_url": "...",
        "customer_info": { "name": "...", "email": "...", "phone": "..." }  # optional
    }
    """
    if not settings.KHALTI_SECRET_KEY:
        return Response(
            {'error': 'Khalti is not configured. Add KHALTI_SECRET_KEY to .env'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    data = request.data
    amount = int(data.get('amount', 0))
    purchase_order_id = data.get('purchase_order_id', str(uuid.uuid4()))
    purchase_order_name = data.get('purchase_order_name', 'Payment')
    return_url = data.get('return_url', '')
    website_url = data.get('website_url', return_url or 'https://example.com')
    customer_info = data.get('customer_info', {})

    if amount < 1000:
        return Response(
            {'error': 'amount must be at least 1000 paisa (Rs 10)'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not return_url:
        return Response(
            {'error': 'return_url is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = {
        'return_url': return_url,
        'website_url': website_url,
        'amount': amount,
        'purchase_order_id': purchase_order_id,
        'purchase_order_name': purchase_order_name,
        'customer_info': customer_info,
    }

    url = f"{_khalti_base_url()}/epayment/initiate/"
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        try:
            resp = r.json()
        except ValueError:
            resp = {'error': r.text or 'Invalid response from Khalti'}

        if r.status_code != 200:
            err = resp if isinstance(resp, dict) else {'error': str(resp)}
            return Response(err, status=r.status_code)

        return Response({
            'pidx': resp.get('pidx'),
            'payment_url': resp.get('payment_url'),
            'expires_at': resp.get('expires_at'),
            'expires_in': resp.get('expires_in'),
        })
    except requests.RequestException as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def khalti_verify(request):
    """
    Verify Khalti payment using pidx.
    Body: { "pidx": "..." }
    """
    if not settings.KHALTI_SECRET_KEY:
        return Response(
            {'error': 'Khalti is not configured. Add KHALTI_SECRET_KEY to .env'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    pidx = request.data.get('pidx', '')
    if not pidx:
        return Response(
            {'error': 'pidx is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    url = f"{_khalti_base_url()}/epayment/lookup/"
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        r = requests.post(url, json={'pidx': pidx}, headers=headers, timeout=10)
        try:
            resp = r.json()
        except ValueError:
            resp = {'error': r.text or 'Invalid response from Khalti'}

        if r.status_code != 200:
            err = resp if isinstance(resp, dict) else {'error': str(resp)}
            return Response(err, status=r.status_code)

        return Response(resp)
    except requests.RequestException as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )
