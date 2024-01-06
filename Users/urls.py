from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CreateUserView, RegisterView, MyProfile, StudentsHome, LoginRedirect, FinishSetup, Login, StaticViewSitemap
from django.contrib.sitemaps.views import sitemap

from Users import views

sitemaps = {
    'static': StaticViewSitemap,
}
urlpatterns = [

    path('Sign-Up/', RegisterView.as_view(), name='register'),
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('Profile/', MyProfile.as_view(), name='update-profile'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('Student/', StudentsHome.as_view(), name='student-home'),
    path('', views.rout, name='rout'),
    path('login-Redirect/', LoginRedirect.as_view(), name='redirect'),
    path('Profile-Set-Up/', FinishSetup.as_view(), name='edit-profile'),
    path('Sign-In/', Login.as_view(), name='login'),
    path('Logout/', auth_views.LogoutView.as_view(template_name='Users/logout.html'), name='logout'),

]
