from django.contrib import messages
from django.core.paginator import Paginator
# type hinting imports
from django.db.models import SlugField
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


def product_detail_view(request: HttpRequest, slug: SlugField) -> HttpResponse:
    product = get_object_or_404(
        ProductProxy.objects.select_related('category'), slug=slug
    )

    if request.method == 'POST':
        if request.user.is_authenticated:
            if product.reviews.filter(created_by=request.user).exists():
                messages.error(
                    request, "You have already made a review for this product."
                )
            else:
                rating = request.POST.get('rating', 3)
                content = request.POST.get('content', '')
                if content:
                    product.reviews.create(
                        rating=rating, content=content, created_by=request.user, product=product
                    )
                    return redirect(request.path)
        else:
            messages.error(
                request, "You need to be logged in to make a review."
            )

    context = {'product': product}
    return render(request, 'shop/product_detail.html', context)


def category_list_view(request: HttpRequest, slug: SlugField) -> HttpResponse:
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
