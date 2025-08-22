import json
from server import app
from .base_test_task_comment import BaseTestTaskComment
from modules.task_comment.types import TaskCommentErrorCode
from modules.authentication.types import AccessTokenErrorCode


class TestTaskCommentAPI(BaseTestTaskComment):
    """Test cases for Task Comment REST API endpoints"""
    
    def test_create_comment_api_success(self):
        """Test POST /api/accounts/{account_id}/tasks/{task_id}/comments - Success"""
        comment_data = {
            "content": "API test comment"
        }
        
        with app.test_client() as client:
            response = client.post(
                self.get_task_comments_api_url(self.test_account.id, self.test_task.id),
                data=json.dumps(comment_data),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        
        assert response.status_code == 201
        
        response_data = response.json
        assert response_data['content'] == comment_data['content']
        assert response_data['task_id'] == self.test_task.id
        assert response_data['account_id'] == self.test_account.id
        assert 'id' in response_data
        assert 'created_at' in response_data
        assert 'updated_at' in response_data
        
    def test_create_comment_api_missing_content(self):
        """Test POST /api/accounts/{account_id}/tasks/{task_id}/comments - Missing content"""
        comment_data = {}
        
        with app.test_client() as client:
            response = client.post(
                self.get_task_comments_api_url(self.test_account.id, self.test_task.id),
                data=json.dumps(comment_data),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        
        assert response.status_code == 400
        assert response.json is not None
        assert 'content' in response.json.get('message', '').lower() or 'errors' in response.json
        
    def test_create_comment_api_unauthorized(self):
        """Test POST /api/accounts/{account_id}/tasks/{task_id}/comments - Unauthorized"""
        comment_data = {
            "content": "Unauthorized comment"
        }
        
        # Request without auth headers
        with app.test_client() as client:
            response = client.post(
                self.get_task_comments_api_url(self.test_account.id, self.test_task.id),
                data=json.dumps(comment_data),
                headers={'Content-Type': 'application/json'}
            )
        
        assert response.status_code == 401
        
    def test_get_comments_api_success(self):
        """Test GET /api/accounts/{account_id}/tasks/{task_id}/comments - Success"""
        # Create additional comments
        for i in range(3):
            self.create_test_comment(f"API comment {i+1}")
            
        with app.test_client() as client:
            response = client.get(
                self.get_task_comments_api_url(self.test_account.id, self.test_task.id),
                headers={'Authorization': f'Bearer {self.test_token}'}
            )
        
        assert response.status_code == 200
        
        response_data = response.json
        assert 'items' in response_data
        assert 'total_count' in response_data
        assert 'pagination_params' in response_data
        assert len(response_data['items']) >= 4  # Including setup comment
        
    def test_get_comments_api_pagination(self):
        """Test GET /api/accounts/{account_id}/tasks/{task_id}/comments - Pagination"""
        # Create multiple comments
        for i in range(5):
            self.create_test_comment(f"Pagination comment {i+1}")
            
        with app.test_client() as client:
            response = client.get(
                f"{self.get_task_comments_api_url(self.test_account.id, self.test_task.id)}?page=1&size=3",
                headers={'Authorization': f'Bearer {self.test_token}'}
            )
        
        assert response.status_code == 200
        
        response_data = response.json
        assert len(response_data['items']) == 3
        assert response_data['pagination_params']['page'] == 1
        assert response_data['pagination_params']['size'] == 3
        assert response_data['total_count'] >= 6  # Including setup comment
        
    def test_update_comment_api_success(self):
        """Test PATCH /api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id} - Success"""
        update_data = {
            "content": "Updated via API"
        }
        
        with app.test_client() as client:
            response = client.patch(
                self.get_task_comment_by_id_api_url(self.test_account.id, self.test_task.id, self.test_comment.id),
                data=json.dumps(update_data),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        
        assert response.status_code == 200
        
        response_data = response.json
        assert response_data['content'] == update_data['content']
        assert response_data['id'] == self.test_comment.id
        
    def test_update_comment_api_not_found(self):
        """Test PATCH /api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id} - Not found"""
        update_data = {
            "content": "Update non-existent comment"
        }
        
        with app.test_client() as client:
            response = client.patch(
                self.get_task_comment_by_id_api_url(self.test_account.id, self.test_task.id, "invalid_comment_id"),
                data=json.dumps(update_data),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        
        assert response.status_code == 404
        
    def test_delete_comment_api_success(self):
        """Test DELETE /api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id} - Success"""
        # Create a comment specifically for deletion
        comment_to_delete = self.create_test_comment("Comment to delete")
        
        with app.test_client() as client:
            response = client.delete(
                self.get_task_comment_by_id_api_url(self.test_account.id, self.test_task.id, comment_to_delete.id),
                headers={'Authorization': f'Bearer {self.test_token}'}
            )
        
        assert response.status_code == 200
        
        response_data = response.json
        assert response_data['success'] == True
        assert response_data['message'] == "Comment deleted successfully"
        
    def test_delete_comment_api_not_found(self):
        """Test DELETE /api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id} - Not found"""
        with app.test_client() as client:
            response = client.delete(
                self.get_task_comment_by_id_api_url(self.test_account.id, self.test_task.id, "invalid_comment_id"),
                headers={'Authorization': f'Bearer {self.test_token}'}
            )
        
        assert response.status_code == 404
        
    def test_api_invalid_task_id(self):
        """Test all endpoints with invalid task ID"""
        invalid_task_id = "invalid_task_id"
        
        # Test GET
        with app.test_client() as client:
            response = client.get(
                self.get_task_comments_api_url(self.test_account.id, invalid_task_id),
                headers={'Authorization': f'Bearer {self.test_token}'}
            )
        assert response.status_code == 404
        
        # Test POST
        with app.test_client() as client:
            response = client.post(
                self.get_task_comments_api_url(self.test_account.id, invalid_task_id),
                data=json.dumps({"content": "Test"}),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        assert response.status_code == 404
        
    def test_api_content_validation(self):
        """Test API content validation"""
        # Test empty content
        with app.test_client() as client:
            response = client.post(
                self.get_task_comments_api_url(self.test_account.id, self.test_task.id),
                data=json.dumps({"content": ""}),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        assert response.status_code == 400
        
        # Test content too long (assuming max length is 1000)
        long_content = "x" * 1001
        with app.test_client() as client:
            response = client.post(
                self.get_task_comments_api_url(self.test_account.id, self.test_task.id),
                data=json.dumps({"content": long_content}),
                headers={
                    'Authorization': f'Bearer {self.test_token}',
                    'Content-Type': 'application/json'
                }
            )
        assert response.status_code == 400