from django.urls import path

from . import views

urlpatterns = [
    path('add/item/', views.add_purchased_item_view, name= 'add_itmes'),
    path('factors/', views.factors_list_view, name='factor_list'),
    path('factors/<int:pk>/', views.factor_detail_view, name='factor_detail'),
    path('invoice/<int:pk>/', views.invoice_pay, name='payment_invoice'),
    path('payment_check/', views.check_payment, name='check_payment'),
]
