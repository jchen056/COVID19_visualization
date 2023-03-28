
from django.urls import path
from .views import HomeView,ArticleDetailView

# from . import views

urlpatterns = [
    # path('', views.home,name="home"),
    path('',HomeView.as_view(),name="home"),
    path('article/<int:pk>',ArticleDetailView.as_view(), name="article-detail"),

]