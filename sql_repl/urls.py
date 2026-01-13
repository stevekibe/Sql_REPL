from django.urls import path
from . import views

urlpatterns = [
    # This maps the root of the app to the index view we created
    path('', views.index, name='repl_index'),
]