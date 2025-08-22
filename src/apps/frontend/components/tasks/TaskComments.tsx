import React, { useState } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useTaskComments, useCreateComment, useUpdateComment, useDeleteComment } from '../../hooks/useTaskComments';
import { TaskComment } from '../../services/task-comments.service';
import { Task } from '../../services/tasks.service';

interface TaskCommentsProps {
  task: Task;
  className?: string;
}

interface CommentItemProps {
  comment: TaskComment;
  taskId: string;
}

const commentValidationSchema = Yup.object({
  content: Yup.string()
    .required('Comment cannot be empty')
    .min(1, 'Comment must have at least 1 character')
    .max(1000, 'Comment must be less than 1000 characters'),
});

const CommentItem: React.FC<CommentItemProps> = ({ comment, taskId }) => {
  const [isEditing, setIsEditing] = useState(false);
  const updateCommentMutation = useUpdateComment(taskId, comment.id);
  const deleteCommentMutation = useDeleteComment(taskId);

  const editFormik = useFormik({
    initialValues: { content: comment.content },
    validationSchema: commentValidationSchema,
    onSubmit: async (values) => {
      try {
        await updateCommentMutation.mutateAsync({ content: values.content });
        setIsEditing(false);
      } catch (error) {
        // Error handling is done in the mutation hook
      }
    },
  });

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      try {
        await deleteCommentMutation.mutateAsync(comment.id);
      } catch (error) {
        // Error handling is done in the mutation hook
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      return diffInMinutes < 1 ? 'Just now' : `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (isEditing) {
    return (
      <div className="comment-item editing">
        <form onSubmit={editFormik.handleSubmit} className="comment-edit-form">
          <textarea
            name="content"
            value={editFormik.values.content}
            onChange={editFormik.handleChange}
            onBlur={editFormik.handleBlur}
            className={`comment-edit-input ${editFormik.touched.content && editFormik.errors.content ? 'error' : ''}`}
            disabled={updateCommentMutation.isPending}
            autoFocus
            rows={3}
          />
          {editFormik.touched.content && editFormik.errors.content && (
            <div className="error-message">{editFormik.errors.content}</div>
          )}
          <div className="comment-edit-actions">
            <button
              type="submit"
              className="btn-primary small"
              disabled={updateCommentMutation.isPending || !editFormik.values.content.trim()}
            >
              {updateCommentMutation.isPending ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={() => {
                setIsEditing(false);
                editFormik.resetForm();
              }}
              className="btn-secondary small"
              disabled={updateCommentMutation.isPending}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="comment-item">
      <div className="comment-content">
        <p>{comment.content}</p>
      </div>
      <div className="comment-meta">
        <span className="comment-date" title={new Date(comment.created_at).toLocaleString()}>
          {formatDate(comment.created_at)}
          {comment.updated_at !== comment.created_at && (
            <span className="edited-indicator"> (edited)</span>
          )}
        </span>
        <div className="comment-actions">
          <button
            onClick={() => setIsEditing(true)}
            className="btn-link small"
            disabled={updateCommentMutation.isPending}
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="btn-link small danger"
            disabled={deleteCommentMutation.isPending}
          >
            {deleteCommentMutation.isPending ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
};

export const TaskComments: React.FC<TaskCommentsProps> = ({ task, className = '' }) => {
  const { data: commentsData, isLoading, error } = useTaskComments(task.id);
  const createCommentMutation = useCreateComment(task.id);

  const formik = useFormik({
    initialValues: { content: '' },
    validationSchema: commentValidationSchema,
    onSubmit: async (values, { resetForm }) => {
      try {
        await createCommentMutation.mutateAsync({ content: values.content });
        resetForm();
      } catch (error) {
        // Error handling is done in the mutation hook
      }
    },
  });

  if (error) {
    return (
      <div className={`task-comments error ${className}`}>
        <div className="error-message">Failed to load comments. Please try again.</div>
      </div>
    );
  }

  return (
    <div className={`task-comments ${className}`}>
      <div className="task-header">
        <h2 className="task-title">{task.title}</h2>
        {task.description && (
          <p className="task-description">{task.description}</p>
        )}
      </div>

      <div className="comments-section">
        <h3 className="comments-title">
          Comments ({commentsData?.total_count || 0})
        </h3>

        <form onSubmit={formik.handleSubmit} className="comment-create-form">
          <textarea
            name="content"
            placeholder="Write a comment..."
            value={formik.values.content}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            className={`comment-input ${formik.touched.content && formik.errors.content ? 'error' : ''}`}
            disabled={createCommentMutation.isPending}
            rows={3}
          />
          {formik.touched.content && formik.errors.content && (
            <div className="error-message">{formik.errors.content}</div>
          )}
          <div className="comment-create-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={createCommentMutation.isPending || !formik.values.content.trim()}
            >
              {createCommentMutation.isPending ? (
                <>
                  <span className="spinner"></span>
                  Adding...
                </>
              ) : (
                'Add Comment'
              )}
            </button>
          </div>
        </form>

        <div className="comments-list">
          {isLoading ? (
            <div className="loading-state">
              <span className="spinner"></span>
              Loading comments...
            </div>
          ) : !commentsData?.comments?.length ? (
            <div className="empty-state">
              <p>No comments yet. Be the first to comment!</p>
            </div>
          ) : (
            commentsData.comments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                taskId={task.id}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};