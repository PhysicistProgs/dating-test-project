from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers
from api_app.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['email', 'first_name',
                  'last_name', 'sex',
                  'avatar', 'password', 'friends', 'pk']
        model = User

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserMatchSerializer(serializers.ModelSerializer):
    friend = serializers.IntegerField(write_only=True)
    friend_mail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'sex', 'friends', 'friend', 'friend_mail']

    def send_mails(self, sender, receiver):
        """
        Отправляет емейлы на почту двум клиентам, у которых случился матч
        """
        for i in range(2):
            mail_theme = 'У вас match!'
            mail_text = f'{sender.first_name} оценил вас! Его почта: {sender.email}'
            send_mail(mail_theme, mail_text, settings.EMAIL_HOST_USER, [receiver.email])
            sender, receiver = receiver, sender

    def update(self, instance, validated_data):
        new_friend_pk = validated_data.pop('friend')
        new_friend = User.objects.get(pk=new_friend_pk)
        if new_friend.pk != instance.pk:  # проверяем, что пользователь не в списке лайкнутых
            instance.friends.add(new_friend)
            if instance in new_friend.friends.all():  # проверка на матч
                self.context['match'] = True
                self.send_mails(instance, new_friend)
        return instance

    def get_friend_mail(self, obj):
        """
        Возвращает емейл лайкнутого пользователя, если случился матч.
        Иначе возвращает None.
        """
        if self.context['match']:
            return User.objects.get(pk=self.context['pk']).email
        return None
