from django.urls import path
from django.conf.urls.static import static
from webserviceApp import views
from webserviceProduct import settings

urlpatterns = [
    # For the Provider CRUD Operator -
    path('create_service/', views.create_service),
    path('get_service/<str:_id>', views.get_service),
    path('update_service/<str:_id>', views.update_service),
    path('delete_service/<str:_id>', views.delete_service),
    path('list_services/', views.list_services),

    # For the LogIn, LogOut and Register -
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),

    # For the Searching Purpose and Book -
    path('search_services/', views.search_services),
    path('book_service/', views.book_service),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)