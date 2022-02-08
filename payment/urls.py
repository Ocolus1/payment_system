from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pay.urls')),
    # path('accounts/', include('allauth.urls')),
]

handler404 = 'pay.views.custom_page_not_found_view'
handler500 = 'pay.views.custom_error_view'
handler403 = 'pay.views.custom_permission_denied_view'
handler401 = 'pay.views.custom_bad_request_view'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)