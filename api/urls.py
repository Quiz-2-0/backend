from django.urls import include, path

urlpatterns = [
    path("admin/", include("admin.urls")),
    path("users/", include("user.urls")),
    path("quizes/", include("quizes.urls")),
]
