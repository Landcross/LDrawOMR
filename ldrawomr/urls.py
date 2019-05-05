from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from ldrawomr import settings
from omr.views import views, ajax_views

urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('statistics', views.statistics, name='statistics'),
    path('files', views.file_list, name='file_list'),
    path('files/<int:file_id>', views.file_detail, name='file_detail'),

    # Ajax urls for filtering
    path('files/ajax/table', ajax_views.file_table),

    # Backwards compatability
    path('file/<int:file_id>', RedirectView.as_view(pattern_name='file_detail', permanent=True)),

    # Admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
