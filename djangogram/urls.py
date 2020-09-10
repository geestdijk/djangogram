from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.urls import include, path, re_path

from . import settings
from my_app.social_auth import views as social_auth_views
from my_app.views import HomePageFeedView

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$", HomePageFeedView.as_view(), name="home"),
    path('', include('my_app.urls')),
]

social_auth_email_patterns = [
    re_path(r'^email/$', social_auth_views.require_email, name='require_email',),
    re_path(r'^email-sent/', social_auth_views.validation_sent),
]

urlpatterns += social_auth_email_patterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    from . import debug_urls
    urlpatterns = debug_urls.urlpatterns + urlpatterns
