"""phx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.static import serve
from error.views import Error400View, Error403View, Error404View, error_500

from .admin import phx_admin

urlpatterns = [
    # app
    path('admin/', phx_admin.urls),
    path('', include('home.urls')),
    path('', include('offline.urls')),
    path('news/', include('news.urls')),
    path('fixtures/', include('fixtures.urls')),
    path('results/', include('results.urls')),
    path('contact/', include('contact.urls')),
    path('gallery/', include('gallery.urls')),
    path('components/', include('components.urls')),

    # third-party
    re_path(r'^_nested_admin/', include('nested_admin.urls')),

    # HACK: serve media from filesystem
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),

    # pages - must be last
    re_path(r'^(?P<slug>.*)/', include('pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = Error400View.as_view()
handler403 = Error403View.as_view()
handler404 = Error404View.as_view()
handler500 = error_500

# debug toolbar
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
