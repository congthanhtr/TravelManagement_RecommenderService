from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('maps', views.maps, name='maps'),
    path('maps_v2', views.maps_v2, name='maps_v2'),
    path("maps_v3", views.maps_v3, name="maps_v3"),
    path('crawl', views.crawl, name='crawl'),
    path('recommend_tour', views.recommend_tour, name='recommend_tour'),
    path('weather_forecast', views.weather_forecast, name='weather_forecast')
]
