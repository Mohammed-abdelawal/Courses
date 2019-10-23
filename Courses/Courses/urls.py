from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include


# -----------TranslationWith i18n----------------

urlpatterns = []
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += i18n_patterns(path('', include('website.urls')))
