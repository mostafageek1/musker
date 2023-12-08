from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('user_search/', views.user_search, name='user_search'),
    path('profile_list/', views.profile_list, name='profile_list'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile/followers/<int:pk>', views.followers, name='followers'),
    path('profile/follows/<int:pk>', views.follows, name='follows'),
    path('update_user/', views.update_user, name='update_user'),
    path('change_password/', views.change_password, name='change_password'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('meep_like/<int:pk>', views.meep_like, name='meep_like'),
    path('meep_share/<int:pk>', views.meep_share, name='meep_share'),
    path('meep_delete/<int:pk>', views.meep_delete, name='meep_delete'),
    path('meep_edit/<int:pk>', views.meep_edit, name='meep_edit'),
]
