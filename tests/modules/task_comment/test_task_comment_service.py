import pytest
from .base_test_task_comment import BaseTestTaskComment
from modules.task_comment.task_comment_service import TaskCommentService
from modules.task_comment.types import (
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams
)
from modules.task_comment.errors import (
    TaskCommentNotFoundError,
    UnauthorizedCommentEditError,
    UnauthorizedCommentDeleteError,
    InvalidCommentContentError,
    TaskNotFoundForCommentError
)
from modules.application.common.types import PaginationParams


class TestTaskCommentService(BaseTestTaskComment):
    """Test cases for Task Comment Service Layer"""
    
    def test_create_comment_success(self):
        """Test successful comment creation"""
        content = "New test comment"
        
        create_params = CreateTaskCommentParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content=content
        )
        
        comment = TaskCommentService.create_comment(create_params)
        
        assert comment is not None
        assert comment.content == content
        assert comment.task_id == self.test_task.id
        assert comment.account_id == self.test_account.id
        assert comment.created_at is not None
        assert comment.updated_at is not None
        
    def test_create_comment_invalid_task(self):
        """Test comment creation with invalid task ID"""
        create_params = CreateTaskCommentParams(
            task_id="invalid_task_id",
            account_id=self.test_account.id,
            content="Test comment"
        )
        
        with pytest.raises(TaskNotFoundForCommentError):
            TaskCommentService.create_comment(create_params)
            
    def test_get_task_comments_success(self):
        """Test successful retrieval of task comments"""
        # Create additional comments        self.create_test_comment("First comment")
        self.create_test_comment("Second comment")
        
        params = GetTaskCommentsParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            pagination_params=PaginationParams(page=1, limit=10)
        )
        
        result = TaskCommentService.get_task_comments(params)
        
        assert result is not None
        assert len(result.comments) >= 3  # Including the one from setup
        assert result.total_count >= 3
        assert result.page == 1
        assert result.limit == 10
        
    def test_get_task_comments_pagination(self):
        """Test comment pagination"""
        # Create multiple comments
        for i in range(5):
            self.create_test_comment(f"Comment {i+1}")
            
        # Test first page
        params = GetTaskCommentsParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            pagination_params=PaginationParams(page=1, limit=3)
        )
        
        result = TaskCommentService.get_task_comments(params)
        
        assert len(result.comments) == 3
        assert result.page == 1
        assert result.limit == 3
        assert result.has_more == True
        
    def test_update_comment_success(self):
        """Test successful comment update"""
        new_content = "Updated comment content"
        
        update_params = UpdateTaskCommentParams(
            comment_id=self.test_comment.id,
            account_id=self.test_account.id,
            content=new_content
        )
        
        updated_comment = TaskCommentService.update_comment(update_params)
        
        assert updated_comment.content == new_content
        assert updated_comment.id == self.test_comment.id
        assert updated_comment.updated_at > self.test_comment.updated_at
        
    def test_update_comment_unauthorized(self):
        """Test comment update by unauthorized user"""
        # Create another account
        other_account = self.create_test_account(
            phone_number="+1234567891",
            email="other@test.com"
        )
        
        update_params = UpdateTaskCommentParams(
            comment_id=self.test_comment.id,
            account_id=other_account.id,
            content="Unauthorized update"
        )
        
        with pytest.raises(UnauthorizedCommentEditError):
            TaskCommentService.update_comment(update_params)
            
    def test_update_comment_not_found(self):
        """Test update of non-existent comment"""
        update_params = UpdateTaskCommentParams(
            comment_id="invalid_comment_id",
            account_id=self.test_account.id,
            content="Updated content"
        )
        
        with pytest.raises(TaskCommentNotFoundError):
            TaskCommentService.update_comment(update_params)
            
    def test_delete_comment_success(self):
        """Test successful comment deletion"""
        comment_id = self.test_comment.id
        
        delete_params = DeleteTaskCommentParams(
            comment_id=comment_id,
            account_id=self.test_account.id
        )
        
        result = TaskCommentService.delete_comment(delete_params)
        
        assert result.success == True
        assert result.comment_id == comment_id
        assert result.message == "Comment deleted successfully"
        
        # Verify comment is actually deleted
        with pytest.raises(TaskCommentNotFoundError):
            TaskCommentService.get_comment(comment_id, self.test_account.id)
            
    def test_delete_comment_unauthorized(self):
        """Test comment deletion by unauthorized user"""
        # Create another account
        other_account = self.create_test_account(
            phone_number="+1234567892",
            email="other2@test.com"
        )
        
        delete_params = DeleteTaskCommentParams(
            comment_id=self.test_comment.id,
            account_id=other_account.id
        )
        
        with pytest.raises(UnauthorizedCommentDeleteError):
            TaskCommentService.delete_comment(delete_params)
            
    def test_delete_comment_not_found(self):
        """Test deletion of non-existent comment"""
        delete_params = DeleteTaskCommentParams(
            comment_id="invalid_comment_id",
            account_id=self.test_account.id
        )
        
        with pytest.raises(TaskCommentNotFoundError):
            TaskCommentService.delete_comment(delete_params)
            
    def test_comment_content_validation(self):
        """Test comment content validation"""
        # Test empty content
        with pytest.raises(ValueError):
            CreateTaskCommentParams(
                task_id=self.test_task.id,
                account_id=self.test_account.id,
                content=""
            )
            
        # Test content too long
        long_content = "x" * 201  # Exceeds 200 character limit
        with pytest.raises(ValueError):
            CreateTaskCommentParams(
                task_id=self.test_task.id,
                account_id=self.test_account.id,
                content=long_content
            )
