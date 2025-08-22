import pytest
import json
from .base_test_task_comment import BaseTestTaskComment
from modules.authentication.internals.access_token.access_token_util import AccessTokenUtil


class TestTaskCommentAPI(BaseTestTaskComment):
    """Test cases for Task Comment REST API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup_api_test(self, app_client):
        """Set up API test with authentication"""
        self.client = app_client
        
        # Generate access token for authentication
        access_token = AccessTokenUtil.generate_access_token(
            account_id=self.test_account.id
        )
        self.auth_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
    def test_create_comment_api_success(self):
        """Test POST /api/tasks/{task_id}/comments - Success"""
        comment_data = {
            "content": "API test comment"
        }
        
        response = self.client.post(
            f'/api/tasks/{self.test_task.id}/comments',
            data=json.dumps(comment_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 201
        
        response_data = json.loads(response.data)
        assert response_data['content'] == comment_data['content']
        assert response_data['task_id'] == self.test_task.id
        assert response_data['account_id'] == self.test_account.id
        assert 'id' in response_data
        assert 'created_at' in response_data
        assert 'updated_at' in response_data
        
    def test_create_comment_api_missing_content(self):
        """Test POST /api/tasks/{task_id}/comments - Missing content"""
        comment_data = {}
        
        response = self.client.post(
            f'/api/tasks/{self.test_task.id}/comments',
            data=json.dumps(comment_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'errors' in response_data
        
    def test_create_comment_api_unauthorized(self):
        """Test POST /api/tasks/{task_id}/comments - Unauthorized"""
        comment_data = {
            "content": "Unauthorized comment"
        }
        
        # Request without auth headers
        response = self.client.post(
            f'/api/tasks/{self.test_task.id}/comments',
            data=json.dumps(comment_data),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 401
        
    def test_get_comments_api_success(self):
        """Test GET /api/tasks/{task_id}/comments - Success"""
        # Create additional comments
        for i in range(3):
            self.create_test_comment(f"API comment {i+1}")
            
        response = self.client.get(
            f'/api/tasks/{self.test_task.id}/comments',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert 'comments' in response_data
        assert 'total_count' in response_data
        assert 'page' in response_data
        assert 'limit' in response_data
        assert 'has_more' in response_data
        assert len(response_data['comments']) >= 4  # Including setup comment
        
    def test_get_comments_api_pagination(self):
        """Test GET /api/tasks/{task_id}/comments - Pagination"""
        # Create multiple comments
        for i in range(5):
            self.create_test_comment(f"Pagination comment {i+1}")
            
        response = self.client.get(
            f'/api/tasks/{self.test_task.id}/comments?page=1&limit=3',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert len(response_data['comments']) == 3
        assert response_data['page'] == 1
        assert response_data['limit'] == 3
        assert response_data['has_more'] == True
        
    def test_update_comment_api_success(self):
        """Test PUT /api/tasks/{task_id}/comments/{comment_id} - Success"""
        update_data = {
            "content": "Updated via API"
        }
        
        response = self.client.put(
            f'/api/tasks/{self.test_task.id}/comments/{self.test_comment.id}',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['content'] == update_data['content']
        assert response_data['id'] == self.test_comment.id
        
    def test_update_comment_api_not_found(self):
        """Test PUT /api/tasks/{task_id}/comments/{comment_id} - Not found"""
        update_data = {
            "content": "Update non-existent comment"
        }
        
        response = self.client.put(
            f'/api/tasks/{self.test_task.id}/comments/invalid_comment_id',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        
    def test_delete_comment_api_success(self):
        """Test DELETE /api/tasks/{task_id}/comments/{comment_id} - Success"""
        # Create a comment specifically for deletion
        comment_to_delete = self.create_test_comment("Comment to delete")
        
        response = self.client.delete(
            f'/api/tasks/{self.test_task.id}/comments/{comment_to_delete.id}',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['success'] == True
        assert response_data['comment_id'] == comment_to_delete.id
        assert response_data['message'] == "Comment deleted successfully"
        
    def test_delete_comment_api_not_found(self):
        """Test DELETE /api/tasks/{task_id}/comments/{comment_id} - Not found"""
        response = self.client.delete(
            f'/api/tasks/{self.test_task.id}/comments/invalid_comment_id',
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        
    def test_api_invalid_task_id(self):
        """Test all endpoints with invalid task ID"""
        invalid_task_id = "invalid_task_id"
        
        # Test GET
        response = self.client.get(
            f'/api/tasks/{invalid_task_id}/comments',
            headers=self.auth_headers
        )
        assert response.status_code == 404
        
        # Test POST
        response = self.client.post(
            f'/api/tasks/{invalid_task_id}/comments',
            data=json.dumps({"content": "Test"}),
            headers=self.auth_headers
        )
        assert response.status_code == 404
        
    def test_api_content_validation(self):
        """Test API content validation"""
        # Test empty content
        response = self.client.post(
            f'/api/tasks/{self.test_task.id}/comments',
            data=json.dumps({"content": ""}),
            headers=self.auth_headers
        )
        assert response.status_code == 400
        
        # Test content too long
        long_content = "x" * 201
        response = self.client.post(
            f'/api/tasks/{self.test_task.id}/comments',
            data=json.dumps({"content": long_content}),
            headers=self.auth_headers
        )
        assert response.status_code == 400
