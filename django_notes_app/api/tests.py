from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Note


class SignupTests(APITestCase):
    """Tests for the user signup endpoint."""

    def test_signup_success(self):
        """Test that a user can successfully sign up and receive a token."""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
        }
        response = self.client.post('/api/signup', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_duplicate_username(self):
        """Test that signing up with an existing username returns a 400 error."""
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post('/api/signup', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Tests for the user login endpoint."""

    def setUp(self):
        """Create a test user."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_login_success(self):
        """Test that a user can log in and receive a token."""
        response = self.client.post('/api/login', {
            'username': 'testuser',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        """Test that login with wrong password returns a 400 error."""
        response = self.client.post('/api/login', {
            'username': 'testuser',
            'password': 'wrongpass',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_login_user_not_found(self):
        """Test that login with a nonexistent username returns a 404 error."""
        response = self.client.post('/api/login', {
            'username': 'nobody',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_missing_data(self):
        """Test that login without required fields returns a 400 error."""
        response = self.client.post('/api/login', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class NoteCRUDTests(APITestCase):
    """Tests for Note CRUD operations."""

    def setUp(self):
        """Create a test user and authenticate."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_create_note(self):
        """Test that an authenticated user can create a note."""
        response = self.client.post('/api/', {'body': 'Test note body'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.data['body'], 'Test note body')

    def test_list_notes(self):
        """Test that an authenticated user can list their notes."""
        Note.objects.create(user=self.user, body='Note 1')
        Note.objects.create(user=self.user, body='Note 2')
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_note(self):
        """Test that an authenticated user can retrieve a specific note."""
        note = Note.objects.create(user=self.user, body='Test note')
        response = self.client.get(f'/api/note/{note.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['body'], 'Test note')

    def test_update_note(self):
        """Test that an authenticated user can update their note."""
        note = Note.objects.create(user=self.user, body='Original body')
        response = self.client.put(
            f'/api/update/{note.id}',
            {'body': 'Updated body'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.body, 'Updated body')

    def test_delete_note(self):
        """Test that an authenticated user can delete their note."""
        note = Note.objects.create(user=self.user, body='Test note')
        response = self.client.delete(f'/api/delete/{note.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)


class OwnershipEnforcementTests(APITestCase):
    """Tests that users cannot access other users' notes."""

    def setUp(self):
        """Create two users and a note belonging to user B."""
        self.user_a = User.objects.create_user(
            username='user_a', password='pass123'
        )
        self.user_b = User.objects.create_user(
            username='user_b', password='pass123'
        )
        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)
        self.note_b = Note.objects.create(
            user=self.user_b, body="User B's note"
        )

    def test_user_a_cannot_retrieve_user_b_note(self):
        """Test that user A gets a 404 when retrieving user B's note."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_a.key}'
        )
        response = self.client.get(f'/api/note/{self.note_b.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_cannot_update_user_b_note(self):
        """Test that user A gets a 404 when updating user B's note."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_a.key}'
        )
        response = self.client.put(
            f'/api/update/{self.note_b.id}',
            {'body': 'Hacked'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_cannot_delete_user_b_note(self):
        """Test that user A gets a 404 when deleting user B's note."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_a.key}'
        )
        response = self.client.delete(f'/api/delete/{self.note_b.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_lists_only_own_notes(self):
        """Test that a user only sees their own notes in the list view."""
        Note.objects.create(user=self.user_a, body="User A's note")
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_a.key}'
        )
        response = self.client.get('/api/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['body'], "User A's note")

    def test_note_isolation_between_users(self):
        """Test that user B does not see user A's notes in the list."""
        Note.objects.create(user=self.user_a, body="User A's note only")
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_b.key}'
        )
        response = self.client.get('/api/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['body'], "User B's note")


class AuthenticationRequiredTests(APITestCase):
    """Tests that protected endpoints require authentication."""

    def setUp(self):
        """Create a test user and a note."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.note = Note.objects.create(
            user=self.user, body='Test note'
        )

    def test_list_notes_requires_auth(self):
        """Test that listing notes without auth returns 401."""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_note_requires_auth(self):
        """Test that creating a note without auth returns 401."""
        response = self.client.post('/api/', {'body': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_note_requires_auth(self):
        """Test that retrieving a note without auth returns 401."""
        response = self.client.get(f'/api/note/{self.note.id}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_note_requires_auth(self):
        """Test that updating a note without auth returns 401."""
        response = self.client.put(
            f'/api/update/{self.note.id}',
            {'body': 'Test'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_note_requires_auth(self):
        """Test that deleting a note without auth returns 401."""
        response = self.client.delete(f'/api/delete/{self.note.id}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
