from django.contrib import admin

from . import models


@admin.register(models.Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payment_status', 'total_price', 'datetime_transaction', 'datetime_created']
    list_filter = ['payment_status', 'datetime_transaction', 'datetime_created']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'datetime_transaction'
    ordering = ['-datetime_transaction']
    readonly_fields = ['datetime_created', 'datetime_modified']


@admin.register(models.PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'factor', 'price', 'payment_status', 'datetime_created']
    list_filter = [ 'payment_status']
    search_fields = ['user__username', 'user__email', 'reference_id']
    readonly_fields = ['datetime_created', 'datetime_modified']


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'factor', 'payment_authority', 'code', 'payment_datetime']
    list_filter = ['payment_datetime']
    search_fields = ['user__username', 'payment_authority', 'code']
    readonly_fields = ['payment_datetime']