from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('login/', views.login_estoque, name='login'),
    path('', views.lista_estoque, name='lista_estoque'),
    path(
        'movimentacao/',
        views.registrar_movimentacao,
        name='registrar_movimentacao'
    ),
]