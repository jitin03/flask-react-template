import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { TaskCommentsService, TaskComment, CreateCommentRequest, UpdateCommentRequest } from '../services/task-comments.service';

// Query keys
export const commentKeys = {
  all: ['comments'] as const,
  lists: () => [...commentKeys.all, 'list'] as const,
  list: (taskId: string, params?: Record<string, any>) => [...commentKeys.lists(), taskId, params] as const,
};

// Hook for fetching task comments
export const useTaskComments = (
  taskId: string,
  params?: {
    page?: number;
    limit?: number;
  },
  options?: {
    enabled?: boolean;
  }
) => {
  return useQuery({
    queryKey: commentKeys.list(taskId, params),
    queryFn: () => TaskCommentsService.getTaskComments(taskId, params),
    enabled: options?.enabled !== false && !!taskId,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

// Hook for creating comments
export const useCreateComment = (taskId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (commentData: CreateCommentRequest) => TaskCommentsService.createComment(taskId, commentData),
    onSuccess: (newComment: TaskComment) => {
      // Invalidate and refetch comments for this task
      queryClient.invalidateQueries({ queryKey: commentKeys.lists() });
      
      // Optimistically update the cache by adding the new comment
      queryClient.setQueryData(
        commentKeys.list(taskId),
        (oldData: any) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            comments: [...oldData.comments, newComment],
            total_count: oldData.total_count + 1,
          };
        }
      );
      
      toast.success('Comment added successfully!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Failed to create comment';
      toast.error(message);
    },
  });
};

// Hook for updating comments
export const useUpdateComment = (taskId: string, commentId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (commentData: UpdateCommentRequest) => 
      TaskCommentsService.updateComment(taskId, commentId, commentData),
    onSuccess: (updatedComment: TaskComment) => {
      // Update the comment in the cache
      queryClient.setQueryData(
        commentKeys.list(taskId),
        (oldData: any) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            comments: oldData.comments.map((comment: TaskComment) =>
              comment.id === commentId ? updatedComment : comment
            ),
          };
        }
      );
      
      toast.success('Comment updated successfully!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Failed to update comment';
      toast.error(message);
    },
  });
};

// Hook for deleting comments
export const useDeleteComment = (taskId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (commentId: string) => TaskCommentsService.deleteComment(taskId, commentId),
    onSuccess: (_, commentId) => {
      // Remove comment from cache
      queryClient.setQueryData(
        commentKeys.list(taskId),
        (oldData: any) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            comments: oldData.comments.filter((comment: TaskComment) => comment.id !== commentId),
            total_count: Math.max(0, oldData.total_count - 1),
          };
        }
      );
      
      toast.success('Comment deleted successfully!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Failed to delete comment';
      toast.error(message);
    },
  });
};