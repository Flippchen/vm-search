from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('csv', views.csv_to_table, name='csv_to_table'),
    path('login', views.ldap_login, name='login'),
    path('logout', views.logout_view, name='logout')

]
