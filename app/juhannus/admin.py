from django.db import models
from django.forms import Textarea
from django.contrib import admin
from django.utils.html import format_html

from juhannus.models import Header, Body, Event, Participant


class HeaderAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'text_monospace']

    def text_monospace(self, obj):
        header = str.replace(obj.text, '\n', '<br/>')
        header = str.replace(header, ' ', '&nbsp;')
        return format_html(f"<code>{header}</code>")

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 120, 'class': 'vLargeTextField'})}
    }


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
