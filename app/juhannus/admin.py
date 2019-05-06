from django.contrib import admin

from juhannus.models import Header, Body, Event, Participant


class HeaderAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'text']


admin.site.register(Header, HeaderAdmin)


class BodyAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'text']


admin.site.register(Body, BodyAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ['year', 'header', 'body', 'result', 'is_final']


admin.site.register(Event, EventAdmin)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'event', 'vote', 'visible', 'created']
    search_fields = ['name']
    list_filter = ['visible', 'event']
    list_editable = ['visible']


admin.site.register(Participant, ParticipantAdmin)
