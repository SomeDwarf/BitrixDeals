from django.urls import path, include

urlpatterns = [
    path('', include('start.urls')),
    path('deals/', include('deals.urls')),
    path('items_qr/', include('items_qr.urls')),
    path('staff/', include('staff.urls')),
]