from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django_email_verification import urls as email_urls

from . import views

urlpatterns = [
    # path('', lambda request: redirect('shop:products', permanent=False)),
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls'), name='shop'),
    path('cart/', include('cart.urls'), name='cart'),
    path('account/', include('account.urls'), name='account'),
    path('email/', include(email_urls), name='email-verification'),
    path('payment/', include('payment.urls'), name='payment'),
    path('recommend/', include('recommend.urls'), name='recommend'),
    path('api/v1/', include('api.urls', namespace='api')),
    path('', views.index, name='index'),
]

if settings.DEBUG:
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)