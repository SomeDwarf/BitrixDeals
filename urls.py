from django.urls import path, include

urlpatterns = [
    path('', include('start.urls')),
    path('deals/', include('deals.urls')),
]