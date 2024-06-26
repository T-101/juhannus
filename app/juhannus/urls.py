from django.urls import path

from juhannus.views import EventView, StatsView

app_name = "juhannus"

urlpatterns = [
    path('<int:year>/', EventView.as_view(), name="event-detail"),
    path('stats/', StatsView.as_view(), name='event-stats'),
    path('', EventView.as_view(), name="event-latest")
]
