"""
URL configuration for Planner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from Plan.views import *
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('airport_search/', airport_search, name='airport_search'),
    path('login/', login_page, name = "login_page"),
    path('register/', register_page, name = "register_page"),
    path('logout/', logout_page, name ="logout_page"),
    path('create_group/', create_group, name='create_group'),
    path('add_member/<int:group_id>/', add_member, name='add_member'),
    path('accounts/', include('allauth.urls')),
    path('home/', home_page, name = "home_page"),
    path('error/', error_page, name = "error_page"),
    path('send_join_request/<int:group_id>/', send_join_request, name='send_join_request'),
    path('leave_group/<int:group_id>/', leave_group, name='leave_group'),
    path('group/<int:group_id>/', group_details, name='group_details'),
]
