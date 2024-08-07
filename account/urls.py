
from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

app_name='accounts'

urlpatterns = [
    path('signup',views.signup , name='signup'),
    path('',views.login , name='login'),
    path('logout/',views.logout , name='logout'),
    path('profile',views.profile , name='profile'),
    path('profile/edit',views.profile_edit , name='profile_edit'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    

    path('users',views.users , name='users'),
    path('profs',views.profs , name='profs'),
    path('U<int:id>',views.update_user , name='update_user'),
    path('Ud<int:id>',views.delete_user , name='delete_user'),
    
    path('P<int:id>',views.update_prof , name='update_prof'),
    path('Pd<int:id>',views.delete_prof , name='delete_prof'),
    path('upload_professeurs/', views.upload_professeurs, name='upload_professeurs'),
]