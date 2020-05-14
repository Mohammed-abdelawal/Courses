from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include
from website.views import attend 

# -----------Translation With i18n and ajax---------------


urlpatterns = [
    path('attend/', attend, name='attend_url'),
    path(r'ckeditor/', include('ckeditor_uploader.urls')),
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += i18n_patterns(path('', include('website.urls')))
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

