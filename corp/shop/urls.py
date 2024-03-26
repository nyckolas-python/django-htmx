from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.products_view, name='products'),
    path('<slug:slug>/', views.product_detail_view, name='product-detail'),
    path('search/<slug:slug>/', views.category_list_view, name='category-list'),
]
