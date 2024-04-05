from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    # path('', products_view, name='products'),
    path('', views.ProductListView.as_view(), name='products'),
    path('search_products/', views.search_products, name='search-products'),
    path('<slug:slug>/', views.product_detail_view, name='product-detail'),
    path('search/<slug:slug>/', views.category_list_view, name='category-list'),
]
