from django.db import models
from stores.models import Store
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'Order {self.id} - {self.store.name} ({self.status})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField()

    class Meta:
        unique_together = ('order', 'product')
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f'{self.product.title} x{self.quantity_requested}'
