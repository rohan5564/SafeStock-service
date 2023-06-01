# Generated by Django 4.2.1 on 2023-05-28 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_finance_user_alter_shop_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfinances',
            name='type',
            field=models.TextField(blank=True, choices=[('profit', 'Ganancia'), ('cost', 'Gasto')], default='profit', null=True),
        ),
        migrations.DeleteModel(
            name='UserSuppliers',
        ),
    ]