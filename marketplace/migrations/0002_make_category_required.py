"""
Migration to make category required for products
"""
from django.db import migrations, models
import django.db.models.deletion


def create_default_category_and_assign(apps, schema_editor):
    """Create a default category and assign it to products without categories."""
    Category = apps.get_model('marketplace', 'Category')
    Product = apps.get_model('marketplace', 'Product')
    
    # Create a default category if it doesn't exist
    default_category, created = Category.objects.get_or_create(
        name='Uncategorized',
        defaults={'description': 'Default category for products without a category'}
    )
    
    # Assign default category to any products without a category
    Product.objects.filter(category__isnull=True).update(category=default_category)


def reverse_migration(apps, schema_editor):
    """Reverse migration - no action needed."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        # First, assign default category to existing products
        migrations.RunPython(create_default_category_and_assign, reverse_migration),
        # Then, make the field required
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.category'),
        ),
    ]



