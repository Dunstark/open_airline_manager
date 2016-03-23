"""open_airline_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from airline_manager import views
from django.contrib.auth.views import login, logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', login, {'template_name': 'registration/login.html'}),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^home/$', views.user_home, name='home'),
    url(r'^register/$', views.register, name='registration'),
    url(r'^register/hub$', views.register_hub, name='registration-hub'),
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^planes/$', views.planes_list, name='planes'),
    url(r'^hub/$', views.buy_hub, name='buy-hub'),
    url(r'^hubs/buy/$', views.buy_hub_save, name='buy-hub-save'),
    url(r'^alliance/$', views.alliance_home, name='alliance-home'),
    url(r'^alliance/(?P<alliance_id>[0-9]+)/$', views.alliance, name='alliance'),
    url(r'^testing/success$', views.test_success, name='test-success'),
    url(r'^hublist/',views.hub_list,name='hublist'),
    url(r'^playerline/$',views.playerline, name='playerline')
]
