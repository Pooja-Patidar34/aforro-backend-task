# Generated migration file

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='products.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='stores.store')),
            ],
            options={
                'verbose_name_plural': 'inventory',
                'unique_together': {('store', 'product')},
            },
        ),
        migrations.AddIndex(
            model_name='inventory',
            index=models.Index(fields=['store'], name='stores_inve_store_i_idx'),
        ),
        migrations.AddIndex(
            model_name='inventory',
            index=models.Index(fields=['product'], name='stores_inve_product_idx'),
        ),
    ]
