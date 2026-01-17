from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('schema_data/', views.schema_data, name='schema_data'),
    path('download_csv/', views.download_csv, name='download_csv'),
]