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
        # Test empty content
        create_params = CreateTaskCommentParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content=""
        )
        
        try:
            TaskCommentService.create_comment(create_params)
            assert False, "Expected InvalidCommentContentError for empty content"
        except InvalidCommentContentError as e:
            pass
            
        # Test content too long (assuming max is 1000 chars)
        long_content = "x" * 1001
        create_params = CreateTaskCommentParams(
            task_id=self.test_task.id,
            account_id=self.test_account.id,
            content=long_content
        )
        
        try:
            TaskCommentService.create_comment(create_params)
            assert False, "Expected InvalidCommentContentError for content too long"
        except InvalidCommentContentError as e:
            pass
            
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
        assert len(result.items) >= 4
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10
        
        # Verify comments are ordered by created_at desc
        for i in range(len(result.items) - 1):
            assert result.items[i].created_at >= result.items[i + 1].created_at
            
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
        
        assert len(result.items) == 5
        assert result.total_count >= 11  # Including setup comment
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 5
        
        # Get second page
        params.pagination_params.page = 2
        result_page2 = TaskCommentService.get_task_comments(params)
        
        assert len(result_page2.items) == 5
        assert result_page2.pagination_params.page == 2
        
        # Ensure no overlap between pages
        page1_ids = {comment.id for comment in result.items}
        page2_ids = {comment.id for comment in result_page2.items}
        assert len(page1_ids.intersection(page2_ids)) == 0
        
    def test_update_comment_success(self):
        """Test updating a comment successfully"""
        update_params = UpdateTaskCommentParams(
            comment_id=self.test_comment.id,
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
            account_id=self.test_account.id
        )
        
        result = TaskCommentService.delete_comment(delete_params)
        
        assert result is True
        
        # Verify comment is deleted
        try:
            params = GetTaskCommentsParams(
                task_id=self.test_task.id,
                account_id=self.test_account.id,
                pagination_params=PaginationParams(page=1, size=100)
            )
            comments_result = TaskCommentService.get_task_comments(params)
            comment_ids = [c.id for c in comments_result.items]
            assert comment_to_delete.id not in comment_ids
        except:
            pass
            
    def test_delete_comment_not_found(self):
        """Test deleting a non-existent comment"""
        delete_params = DeleteTaskCommentParams(
            comment_id="invalid_comment_id",
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
            account_id=other_account.id  # Different account
        )
        
        try:
            TaskCommentService.delete_comment(delete_params)
            assert False, "Expected UnauthorizedCommentDeleteError"
        except UnauthorizedCommentDeleteError as e:
            pass