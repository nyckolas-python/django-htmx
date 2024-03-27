from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .models import Category, ProductProxy


# def products_view(request: HttpRequest) -> HttpResponse:
#     products = ProductProxy.objects.all()
#     context = {'products': products}
#     return render(request, 'shop/products.html', context)
class ProductListView(ListView):
    model = ProductProxy
    context_object_name = "products"
    paginate_by = 15

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return "shop/components/product_list.html"
        return "shop/products.html"


def product_detail_view(request, slug):
    product = get_object_or_404(ProductProxy, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product})


def category_list_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    product = ProductProxy.objects.select_related('category').filter(category=category)
    context = {'category': category, 'products': product}
    return render(request, 'shop/category_list.html', context=context)

def search_products(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q')
    if not query:
        return redirect('shop:products')

    products = ProductProxy.objects.filter(title__icontains=query).distinct()
    context = {'products': products, 'searching_query': query}

    return render(request, 'shop/products.html', context)
