from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.urls import include, path, re_path

from . import settings
from my_app.views import HomePageFeedView

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$", HomePageFeedView.as_view(), name="home"),
    path('', include('my_app.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
