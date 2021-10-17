import django_filters.rest_framework as filters
from math import pi, sin, asin, sqrt, cos
from api_app.models import User


class FilterUser(filters.FilterSet):
    """
    Фильтры: по полу, имени, фамилии и дистанции на основе модели User.
    Если пользователь не аутентифицирован, фильтр будет по дистанции от центра Новосибирска
    """
    distance = filters.NumberFilter(method='distance_filter', )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'sex',]

    def distance_filter(self, queryset, name, value):
        """
        Фильтр пользователей по дистанции.
        """
        user = self.request.user
        q_pks = (obj.pk for obj in queryset if obj.count_distance(user) < value)
        return queryset.filter(pk__in=q_pks)
