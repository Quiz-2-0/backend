from django.urls import path, include


urlpatterns = [
    path('admin/', include('admin.urls')),
    path('users/', include('user.urls')),
    path('quizes/', include('quizes.urls'))
]
