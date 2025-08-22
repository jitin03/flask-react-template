from datetime import datetime
from .base_test_task_comment import BaseTestTaskComment
from modules.task_comment.task_comment_service import TaskCommentService
from modules.task_comment.types import (
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams,
    TaskCommentErrorCode
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
    """Test cases for Task Comment Service layer"""
    
    def test_create_comment_success(self):
        """Test creating a comment successfully"""
        create_params = CreateTaskCommentParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content="New test comment from service"
        )
        
        comment = TaskCommentService.create_comment(create_params)
        
        assert comment is not None
        assert comment.task_id == self.test_task.id
        assert comment.account_id == self.test_account.id
        assert comment.content == "New test comment from service"
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.updated_at, datetime)
        
    def test_create_comment_invalid_task(self):
        """Test creating a comment for non-existent task"""
        create_params = CreateTaskCommentParams(
            task_id="invalid_task_id",
            account_id=self.test_account.id,
            content="Comment for invalid task"
        )
        
        try:
            TaskCommentService.create_comment(create_params)
            assert False, "Expected TaskNotFoundForCommentError"
        except TaskNotFoundForCommentError as e:
            pass
            
    def test_comment_content_validation(self):
        """Test comment content validation"""
        # Test empty content - should raise ValidationError from Pydantic
        try:
            create_params = CreateTaskCommentParams(
                task_id=self.test_task.id,
                account_id=self.test_account.id,
                content=""
            )
            assert False, "Expected ValidationError for empty content"
        except Exception as e:
            # Pydantic validation error
            assert "content" in str(e).lower()
            
        # Test content too long (max is 200 chars based on type definition)
        long_content = "x" * 201
        try:
            create_params = CreateTaskCommentParams(
                task_id=self.test_task.id,
                account_id=self.test_account.id,
                content=long_content
            )
            assert False, "Expected ValidationError for content too long"
        except Exception as e:
            # Pydantic validation error
            assert "content" in str(e).lower() or "length" in str(e).lower()
            
    def test_get_task_comments_success(self):
        """Test retrieving comments for a task"""
        # Create additional comments
        for i in range(3):
            self.create_test_comment(f"Service test comment {i+1}")
            
        params = GetTaskCommentsParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            pagination_params=PaginationParams(page=1, size=10)
        )
        
        result = TaskCommentService.get_task_comments(params)
        
        assert result.total_count >= 4  # Including setup comment
        assert len(result.comments) >= 4
        assert result.page == 1
        assert result.limit == 10
        
        # Verify comments are ordered by created_at desc
        for i in range(len(result.comments) - 1):
            assert result.comments[i].created_at >= result.comments[i + 1].created_at
            
    def test_get_task_comments_pagination(self):
        """Test pagination when retrieving comments"""
        # Create multiple comments
        for i in range(10):
            self.create_test_comment(f"Pagination test comment {i+1}")
            
        # Get first page
        params = GetTaskCommentsParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            pagination_params=PaginationParams(page=1, size=5)
        )
        
        result = TaskCommentService.get_task_comments(params)
        
        assert len(result.comments) == 5
        assert result.total_count >= 11  # Including setup comment
        assert result.page == 1
        assert result.limit == 5
        
        # Get second page
        params_page2 = GetTaskCommentsParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            pagination_params=PaginationParams(page=2, size=5)
        )
        result_page2 = TaskCommentService.get_task_comments(params_page2)
        
        assert len(result_page2.comments) == 5
        assert result_page2.page == 2
        
        # Ensure no overlap between pages
        page1_ids = {comment.id for comment in result.comments}
        page2_ids = {comment.id for comment in result_page2.comments}
        assert len(page1_ids.intersection(page2_ids)) == 0
        
    def test_update_comment_success(self):
        """Test updating a comment successfully"""
        update_params = UpdateTaskCommentParams(
            comment_id=self.test_comment.id,
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content="Updated comment content from service"
        )
        
        updated_comment = TaskCommentService.update_comment(update_params)
        
        assert updated_comment.id == self.test_comment.id
        assert updated_comment.content == "Updated comment content from service"
        assert updated_comment.updated_at > self.test_comment.updated_at
        
    def test_update_comment_not_found(self):
        """Test updating a non-existent comment"""
        update_params = UpdateTaskCommentParams(
            comment_id="invalid_comment_id",
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content="Updated content"
        )
        
        try:
            TaskCommentService.update_comment(update_params)
            assert False, "Expected TaskCommentNotFoundError"
        except TaskCommentNotFoundError as e:
            pass
            
    def test_update_comment_unauthorized(self):
        """Test updating a comment by different user"""
        # Create another account
        other_account, _ = self.create_account_and_get_token(
            username="other_user@example.com"
        )
        
        update_params = UpdateTaskCommentParams(
            comment_id=self.test_comment.id,
            task_id=self.test_task.id,
            account_id=other_account.id,  # Different account
            content="Unauthorized update"
        )
        
        try:
            TaskCommentService.update_comment(update_params)
            assert False, "Expected UnauthorizedCommentEditError"
        except UnauthorizedCommentEditError as e:
            pass
            
    def test_delete_comment_success(self):
        """Test deleting a comment successfully"""
        # Create a comment specifically for deletion
        comment_to_delete = self.create_test_comment("Comment to delete")
        
        delete_params = DeleteTaskCommentParams(
            comment_id=comment_to_delete.id,
            task_id=self.test_task.id,
            account_id=self.test_account.id
        )
        
        result = TaskCommentService.delete_comment(delete_params)
        
        # The service should return a success response or True
        assert result is not None
            
    def test_delete_comment_not_found(self):
        """Test deleting a non-existent comment"""
        delete_params = DeleteTaskCommentParams(
            comment_id="invalid_comment_id",
            task_id=self.test_task.id,
            account_id=self.test_account.id
        )
        
        try:
            TaskCommentService.delete_comment(delete_params)
            assert False, "Expected TaskCommentNotFoundError"
        except TaskCommentNotFoundError as e:
            pass
            
    def test_delete_comment_unauthorized(self):
        """Test deleting a comment by different user"""
        # Create another account
        other_account, _ = self.create_account_and_get_token(
            username="other_user2@example.com"
        )
        
        delete_params = DeleteTaskCommentParams(
            comment_id=self.test_comment.id,
            task_id=self.test_task.id,
            account_id=other_account.id  # Different account
        )
        
        try:
            TaskCommentService.delete_comment(delete_params)
            assert False, "Expected UnauthorizedCommentDeleteError"
        except UnauthorizedCommentDeleteError as e:
            pass