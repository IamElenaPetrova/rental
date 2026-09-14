from django.urls import path

from public import views

app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('autos/', views.car_list, name='car_list'),
    path('autos/<slug:slug>/', views.car_detail, name='car_detail'),
    path('casas/', views.house_list, name='house_list'),
    path('casas/<slug:slug>/', views.house_detail, name='house_detail'),
]
