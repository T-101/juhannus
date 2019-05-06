from django.urls import path

from juhannus.views import EventView

app_name = "juhannus"

urlpatterns = [
    path('<int:year>/', EventView.as_view(), name="event-detail"),
    path('', EventView.as_view(), name="event-latest")
]
