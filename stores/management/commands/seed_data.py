from django.core.management.base import BaseCommand
from faker import Faker
from products.models import Category, Product
from stores.models import Store, Inventory
import random


class Command(BaseCommand):
    help = 'Seed the database with test data'

    def handle(self, *args, **options):
        fake = Faker()
        self.stdout.write('Seeding database...')

        self.stdout.write('Creating categories...')
        categories = []
        category_names = [
            'Electronics', 'Clothing', 'Food & Beverages', 'Books', 'Home & Garden',
            'Sports', 'Toys', 'Beauty', 'Furniture', 'Automotive', 'Office Supplies', 'Garden'
        ]
        for name in category_names:
            cat, created = Category.objects.get_or_create(name=name)
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        self.stdout.write('Creating products...')
        products = []
        for i in range(1000):
            product = Product.objects.create(
                title=fake.word().title() + ' ' + fake.word().title(),
                description=fake.sentence(),
                price=round(random.uniform(10, 1000), 2),
                category=random.choice(categories)
            )
            products.append(product)
            if (i + 1) % 100 == 0:
                self.stdout.write(f'Created {i + 1} products...')
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

        self.stdout.write('Creating stores...')
        stores = []
        for i in range(20):
            store = Store.objects.create(
                name=fake.company(),
                location=fake.address()
            )
            stores.append(store)
        self.stdout.write(self.style.SUCCESS(f'Created {len(stores)} stores'))

        self.stdout.write('Creating inventory...')
        inventory_count = 0
        for store in stores:
            sample_products = random.sample(products, min(300, len(products)))
            for product in sample_products:
                Inventory.objects.get_or_create(
                    store=store,
                    product=product,
                    defaults={'quantity': random.randint(1, 100)}
                )
                inventory_count += 1
        self.stdout.write(self.style.SUCCESS(f'Created {inventory_count} inventory entries'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
