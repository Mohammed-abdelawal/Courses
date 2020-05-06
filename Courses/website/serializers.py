from rest_framework import serializers
from . import models

# Your Serializers


class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'user', 'article', 'comment', 'time')


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title', 'slug', 'pub_date', 'user', 'pic', 'article',
                  'approved', 'category', 'comments_num')
        read_only_fields = ['id', 'pub_date', 'user']


class ArticleSerializer_create(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'slug', 'user', 'pic', 'cropping', 'article',
                  'category')
        read_only_fields = ['user']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'desc', 'pic', 'cropping', 'articles_num')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'groups', 'is_staff', 'is_superuser', 'last_login',
                  'profile')

    def create(self, validated_data):
        profile = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile)
        return user

    def update(self, instance, validated_data):
        profile_serializer = self.fields['profile']
        profile_instance = instance.profile
        profile_data = validated_data.pop('profile')
        profile_serializer.update(profile_instance, profile_data)
        return super(UserSerializer, self).update(instance, validated_data)
