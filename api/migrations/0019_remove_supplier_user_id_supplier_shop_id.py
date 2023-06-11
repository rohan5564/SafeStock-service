# Generated by Django 4.2.1 on 2023-06-11 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_rename_shop_shopitemsold_shop_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplier',
            name='user_id',
        ),
        migrations.AddField(
            model_name='supplier',
            name='shop_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier', to='api.shop'),
        ),
    ]