from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart-view'),
    path('add/', views.cart_add, name='add-to-cart'),
    path('delete/', views.cart_delete, name='delete-to-cart'),
    path('update/', views.cart_update, name='update-to-cart'),
]
