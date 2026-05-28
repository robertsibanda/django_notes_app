from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics

from .serializers import UserSerializer, NoteSerializer
from .models import Note


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


@api_view(["POST"])
def login(request, *args, **kwargs):
    try:
        username = request.data['username']
        password = request.data['password']

        user = get_object_or_404(User, username=username)
        if not user.check_password(password):
            return Response({"error": "invalid credentials"})

        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    except KeyError:
        return Response({"error": "missing request data"})


@api_view(["POST"])
def signup(request, *args, **kwargs):
    data = {
        'username': request.data['username'],
        'password': request.data['password'],
        'email': request.data.get('email', ''),
    }

    serializer = UserSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        user = User.objects.get(username=data['username'])
        user.set_password(data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key})


class NoteListCreateView(generics.ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


list_create_notes = NoteListCreateView.as_view()


class NoteDeleteView(generics.DestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    permission_classes = [IsAuthenticated, IsOwner]

    def perform_destroy(self, instance):
        instance.delete()


note_delete_view = NoteDeleteView.as_view()


class NoteUpdateView(generics.UpdateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    
note_update_view = NoteUpdateView.as_view()


class NoteDetailView(generics.RetrieveAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOwner]


note_detail_view = NoteDetailView.as_view()

