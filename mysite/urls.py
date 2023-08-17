from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

admin.site.site_header = "nFactorial School Dashboard 💎"

urlpatterns = [
    #
    path("", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("polls/", include("polls.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    #
]
