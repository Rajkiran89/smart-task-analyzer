
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # This connects the main project to your analyzer app
    path('api/tasks/', include('analyzer.urls')),
    # This will show the frontend (which we will build next)
    path('', TemplateView.as_view(template_name='index.html')),
]