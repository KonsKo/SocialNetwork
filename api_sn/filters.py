import django_filters

from .models import Emotion


class AnalyticsFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created__date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created__date', lookup_expr='lt')

    class Meta:
        model = Emotion
        fields = ['date_from', 'date_to']