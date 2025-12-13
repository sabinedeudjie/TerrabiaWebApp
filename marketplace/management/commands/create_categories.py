"""
Management command to create default product categories
"""
from django.core.management.base import BaseCommand
from marketplace.models import Category


class Command(BaseCommand):
    help = 'Creates default product categories for Terrabia'

    def handle(self, *args, **options):
        """Create default categories."""
        categories = [
            'Vegetables',
            'Fruits',
            'Grains & Cereals',
            'Legumes',
            'Tubers & Roots',
            'Spices & Herbs',
            'Nuts & Seeds',
            'Dairy Products',
            'Poultry & Eggs',
            'Livestock',
            'Honey & Bee Products',
            'Other'
        ]
        
        created_count = 0
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully processed {len(categories)} categories. {created_count} new categories created.')
        )



