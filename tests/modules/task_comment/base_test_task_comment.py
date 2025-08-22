from datetime import datetime
from tests.modules.task.base_test_task import BaseTestTask
from modules.task_comment.types import (
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams,
    TaskCommentFilters
)
from modules.task_comment.task_comment_service import TaskCommentService
from modules.task_comment.internal.store.task_comments import TaskCommentRepository
from modules.task_comment.rest_api.task_comment_rest_api_server import TaskCommentRestApiServer
from modules.application.common.types import PaginationParams


class BaseTestTaskComment(BaseTestTask):
    """Base test class for task comment functionality"""
    
    def setUp(self) -> None:
        """Set up test data for task comment tests"""
        super().setUp()
        
        # Create task comment REST API server
        TaskCommentRestApiServer.create()
        
        # Create test account and token
        self.test_account, self.test_token = self.create_account_and_get_token()
        
        # Create test task
        self.test_task = self.create_test_task(
            account_id=self.test_account.id,
            title="Test Task for Comments",
            description="This is a test task for comment testing"
        )
        
        # Create a test comment
        self.test_comment_content = "This is a test comment for the task"
        self.updated_comment_content = "This is an updated test comment"
        
        # Create comment via service
        create_params = CreateTaskCommentParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content=self.test_comment_content
        )
        
        self.test_comment = TaskCommentService.create_comment(create_params)
        
    def tearDown(self) -> None:
        """Clean up test data"""
        TaskCommentRepository.collection().delete_many({})
        super().tearDown()
        
    def create_test_comment(self, content: str = None, task_id: str = None, account_id: str = None):
        """Helper method to create a test comment"""
        content = content or "Test comment content"
        task_id = task_id or self.test_task.id
        account_id = account_id or self.test_account.id
        
        create_params = CreateTaskCommentParams(
            task_id=task_id,
            account_id=account_id,
            content=content
        )
        
        return TaskCommentService.create_comment(create_params)
        
    def get_test_comments(self, task_id: str = None, account_id: str = None, page: int = 1, limit: int = 20):
        """Helper method to get comments for a task"""
        task_id = task_id or self.test_task.id
        account_id = account_id or self.test_account.id
        
        params = GetTaskCommentsParams(
            task_id=task_id,
            account_id=account_id,
            pagination_params=PaginationParams(page=page, limit=limit)
        )
        
        return TaskCommentService.get_task_comments(params)
        
    # URL HELPER METHODS
    
    def get_task_comments_api_url(self, account_id: str, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/tasks/{task_id}/comments"
    
    def get_task_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"http://127.0.0.1:8080/api/tasks/{task_id}/comments/{comment_id}"
