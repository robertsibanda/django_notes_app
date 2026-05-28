from django.contrib.auth.models import User

from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for the Note model."""

    class Meta:
        model = Note
        fields = [
            'id',
            'body',
            'created',
            'updated',
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model during registration."""

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
