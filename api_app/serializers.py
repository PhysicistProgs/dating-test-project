from rest_framework import serializers
from api_app.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['email', 'first_name',
                  'last_name', 'sex',
                  'avatar', 'password',]
        model = User

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
