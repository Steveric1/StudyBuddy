from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('register/', views.registerView, name='register'),
    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.userProfile, name='profile'),
    path('create_room/', views.create_room, name='create_room'),
    path('update_room/<str:pk>/', views.updateRoom, name='update_room'),
    path('delete_room/<str:pk>/', views.deleteRoom, name='delete_room'),
    path('delete_message/<str:pk>/', views.deleteMessage, name='delete_message'),
    path('update-user/', views.updateUser, name='update-user'),
    path('topics/', views.topicsView, name='topics'),
    path('activities/', views.activitiesView, name='activities'),
]