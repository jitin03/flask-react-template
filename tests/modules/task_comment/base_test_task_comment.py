import pytest
from datetime import datetime
from tests.modules.task.base_test_task import BaseTestTask
from tests.modules.account.base_test_account import BaseTestAccount
from modules.task_comment.types import (
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams,
    TaskCommentFilters
)
from modules.task_comment.task_comment_service import TaskCommentService
from modules.application.common.types import PaginationParams


class BaseTestTaskComment(BaseTestTask, BaseTestAccount):
    """Base test class for task comment functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_comment_test_data(self):
        """Set up test data for task comment tests"""
        super().setup_task_test_data()
        
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
