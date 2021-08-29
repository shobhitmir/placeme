"""placeme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from base.views import index_view,login_handle_view,student_cred_view,company_view,profile_view,academics_view,createform_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('home/',login_handle_view,name='loginhandle'),
    path('student-cred/',student_cred_view,name='student_cred'),
    path('companies/',company_view,name='company'),
    path('profile/',profile_view,name='profile'),
    path('academics/',academics_view,name='academics'),
    path('create-form/',createform_view,name='createform'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
