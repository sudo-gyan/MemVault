from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from user.models import Organization, Team, TeamMembership
from memories.models import UserMemory, TeamMemory, OrganizationMemory

User = get_user_model()


class MemoryAPITest(APITestCase):
    """Test the Memory API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.admin_user = User.objects.create_user(username='admin', password='testpass123')
        
        # Create organization and team
        self.organization = Organization.objects.create(
            name='Test Org',
            admin=self.admin_user
        )
        
        self.team = Team.objects.create(
            name='Test Team',
            organization=self.organization
        )
        
        # Add users to team
        TeamMembership.objects.create(user=self.user1, team=self.team)
        TeamMembership.objects.create(user=self.user2, team=self.team)
        
        # Create test memories
        self.user_memory = UserMemory.objects.create(
            user=self.user1,
            content='User memory content'
        )
        
        self.team_memory = TeamMemory.objects.create(
            team=self.team,
            content='Team memory content'
        )
        
        self.org_memory = OrganizationMemory.objects.create(
            organization=self.organization,
            content='Organization memory content'
        )
        
        self.client = APIClient()
    
    def test_user_can_access_own_memories(self):
        """Test that users can access their own memories."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/memories/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'User memory content')
    
    def test_user_cannot_access_other_user_memories(self):
        """Test that users cannot access other users' memories."""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.get('/api/memories/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_team_members_can_access_team_memories(self):
        """Test that team members can access team memories."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/memories/teams/{self.team.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Team memory content')
    
    def test_org_admin_can_access_org_memories(self):
        """Test that org admins can access organization memories."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/memories/orgs/{self.organization.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Organization memory content')
    
    def test_create_user_memory(self):
        """Test creating a new user memory."""
        self.client.force_authenticate(user=self.user1)
        
        data = {'content': 'New user memory'}
        response = self.client.post('/api/memories/users/me/', data)
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New user memory')
        self.assertEqual(UserMemory.objects.filter(user=self.user1).count(), 2)
    
    def test_create_team_memory(self):
        """Test creating a new team memory."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'content': 'New team memory',
            'team': self.team.id
        }
        response = self.client.post(f'/api/memories/teams/{self.team.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New team memory')
        self.assertEqual(TeamMemory.objects.filter(team=self.team).count(), 2)
    
    def test_filtering_by_status(self):
        """Test filtering memories by processing status."""
        self.client.force_authenticate(user=self.user1)
        
        # Create memory with specific status
        UserMemory.objects.create(
            user=self.user1,
            content='Completed memory',
            status='completed'
        )
        
        response = self.client.get('/api/memories/users/me/?status=completed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Completed memory')
    
    def test_search_in_content(self):
        """Test searching memories by content."""
        self.client.force_authenticate(user=self.user1)
        
        UserMemory.objects.create(
            user=self.user1,
            content='This is a special memory about cats'
        )
        
        response = self.client.get('/api/memories/users/me/?search=cats')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('cats', response.data['results'][0]['content'])
