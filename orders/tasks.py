from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
def send_order_confirmation(order_id):
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Confirmation - Order #{order.id}'
        message = f'''
        Your order has been confirmed!

        Order ID: {order.id}
        Store: {order.store.name}
        Status: {order.status}
        Created: {order.created_at}

        Items:
        '''
        for item in order.items.all():
            message += f'\n- {item.product.title} x {item.quantity_requested}'

        send_mail(
            subject,
            message,
            'noreply@aforro.com',
            ['customer@example.com'],
            fail_silently=True,
        )
    except Order.DoesNotExist:
        pass


@shared_task
def generate_inventory_summary():
    from common.models import Inventory
    from django.db.models import Sum

    summary = Inventory.objects.values('store__name').annotate(
        total_quantity=Sum('quantity')
    )
    return list(summary)
