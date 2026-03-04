import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['GET'])
@permission_classes([AllowAny])
def get_publishable_key(request):
    """Return Stripe publishable key for frontend"""
    return Response({
        'publishableKey': settings.STRIPE_PUBLISHABLE_KEY
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    """
    Create a Stripe Checkout Session.
    Body: { "price_id": "price_xxx", "success_url": "...", "cancel_url": "...", "quantity": 1 }
    Or: { "amount": 1000, "currency": "usd", "success_url": "...", "cancel_url": "..." }
    amount is in cents (e.g. 1000 = $10.00)
    """
    if not settings.STRIPE_SECRET_KEY:
        return Response({
            'error': 'Stripe is not configured. Add STRIPE_SECRET_KEY to .env'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        data = request.data
        success_url = data.get('success_url', 'http://localhost:3000/payment/success')
        cancel_url = data.get('cancel_url', 'http://localhost:3000/payment/cancel')
        customer_email = data.get('customer_email', '')
        metadata = data.get('metadata', {})

        # Option 1: Use Price ID (Stripe product/price)
        price_id = data.get('price_id')
        if price_id:
            session_params = {
                'payment_method_types': ['card'],
                'line_items': [{
                    'price': price_id,
                    'quantity': data.get('quantity', 1),
                }],
                'mode': 'payment',
                'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
                'cancel_url': cancel_url,
                'metadata': metadata,
            }
        else:
            # Option 2: Custom amount (one-time payment)
            amount = int(data.get('amount', 0))  # in cents
            currency = data.get('currency', settings.STRIPE_CURRENCY)
            if amount <= 0:
                return Response({
                    'error': 'amount is required and must be greater than 0 (in cents)'
                }, status=status.HTTP_400_BAD_REQUEST)

            session_params = {
                'payment_method_types': ['card'],
                'line_items': [{
                    'price_data': {
                        'currency': currency,
                        'unit_amount': amount,
                        'product_data': {
                            'name': data.get('product_name', 'Payment'),
                            'description': data.get('description', ''),
                        },
                    },
                    'quantity': data.get('quantity', 1),
                }],
                'mode': 'payment',
                'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
                'cancel_url': cancel_url,
                'metadata': metadata,
            }

        if customer_email:
            session_params['customer_email'] = customer_email

        session = stripe.checkout.Session.create(**session_params)

        return Response({
            'sessionId': session.id,
            'url': session.url,
        }, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({
            'error': str(e.user_message) if hasattr(e, 'user_message') else str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_intent(request):
    """
    Create a Payment Intent for custom payment form.
    Body: { "amount": 1000, "currency": "usd" }
    amount is in cents.
    """
    if not settings.STRIPE_SECRET_KEY:
        return Response({
            'error': 'Stripe is not configured. Add STRIPE_SECRET_KEY to .env'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        amount = int(request.data.get('amount', 0))
        currency = request.data.get('currency', settings.STRIPE_CURRENCY)
        if amount <= 0:
            return Response({
                'error': 'amount is required and must be greater than 0 (in cents)'
            }, status=status.HTTP_400_BAD_REQUEST)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True},
            metadata=request.data.get('metadata', {}),
        )

        return Response({
            'clientSecret': intent.client_secret,
            'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
        }, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({
            'error': str(e.user_message) if hasattr(e, 'user_message') else str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks (payment completed, etc.)"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        return HttpResponse('Webhook secret not configured', status=500)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse('Invalid payload', status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse('Invalid signature', status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Payment successful - update your database, send confirmation, etc.
        # session['payment_status'], session['customer_email'], session['metadata']
        pass

    elif event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        # Payment succeeded - update your database
        pass

    return HttpResponse(status=200)
