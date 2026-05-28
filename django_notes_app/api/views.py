from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics

from .serializers import UserSerializer, NoteSerializer
from .models import Note


@api_view(["POST"])
def login(request, *args, **kwargs):
    """Authenticate a user and return an auth token."""
    try:
        username = request.data['username']
        password = request.data['password']

        user = get_object_or_404(User, username=username)
        if not user.check_password(password):
            return Response(
                {"error": "invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    except KeyError:
        return Response(
            {"error": "missing request data"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def signup(request, *args, **kwargs):
    """Register a new user and return an auth token."""
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
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class NoteListCreateView(generics.ListCreateAPIView):
    """List all notes for the authenticated user or create a new note."""

    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter notes to only return those belonging to the requesting user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate the new note with the requesting user."""
        serializer.save(user=self.request.user)


list_create_notes = NoteListCreateView.as_view()


class NoteDeleteView(generics.DestroyAPIView):
    """Delete a note (owner only)."""

    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only notes belonging to the requesting user."""
        return Note.objects.filter(user=self.request.user)


note_delete_view = NoteDeleteView.as_view()


class NoteUpdateView(generics.UpdateAPIView):
    """Update a note (owner only)."""

    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only notes belonging to the requesting user."""
        return Note.objects.filter(user=self.request.user)


note_update_view = NoteUpdateView.as_view()


class NoteDetailView(generics.RetrieveAPIView):
    """Retrieve a single note (owner only)."""

    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only notes belonging to the requesting user."""
        return Note.objects.filter(user=self.request.user)


note_detail_view = NoteDetailView.as_view()

