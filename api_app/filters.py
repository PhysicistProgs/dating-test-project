import django_filters.rest_framework as filters

from api_app.models import User


class FilterUser(filters.FilterSet):
    """
    Фильтры: по полу, имени, фамилии на основе модели User.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'sex']
