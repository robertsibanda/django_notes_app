from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics

from .serializers import UserSerializer, NoteSerializer
from .models import Note


@api_view(["POST"])
def login(request, *args, **kwargs):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"error": "user not found"})

    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["POST"])
def signup(request, *args, **kwargs):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
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
        # save note with user = currently authenticated user
        self.request.data['user'] = self.request.user
        serializer = NoteSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=self.request.user)
        return Response({"success": "note created"})


list_creat_notes = NoteListCreateView.as_view()


class NoteDeleteView(generics.DestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    permission_classes =[IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            instance.delete()
            return Response({"success": "note deleted"})


note_delete_view = NoteDeleteView.as_view()


class NoteUpdateView(generics.UpdateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


note_update_view = NoteUpdateView.as_view()


class NoteDetailView(generics.RetrieveAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


note_detail_view = NoteDetailView.as_view()

