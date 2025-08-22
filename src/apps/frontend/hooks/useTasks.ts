import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  TasksService,
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
} from '../services/tasks.service';

// Query keys
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (accountId: string, filters?: Record<string, any>) =>
    [...taskKeys.lists(), accountId, filters] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (accountId: string, taskId: string) =>
    [...taskKeys.details(), accountId, taskId] as const,
};

// Hook for fetching tasks
export const useTasks = (
  accountId: string,
  params?: {
    page?: number;
    per_page?: number;
  },
  options?: {
    enabled?: boolean;
  },
) => {
  return useQuery({
    queryKey: taskKeys.list(accountId, params),
    queryFn: () => TasksService.getTasks(accountId, params),
    enabled: options?.enabled !== false && !!accountId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// Hook for fetching a single task
export const useTask = (
  accountId: string,
  taskId: string,
  options?: { enabled?: boolean },
) => {
  return useQuery({
    queryKey: taskKeys.detail(accountId, taskId),
    queryFn: () => TasksService.getTask(accountId, taskId),
    enabled: options?.enabled !== false && !!accountId && !!taskId,
  });
};

// Hook for creating tasks
export const useCreateTask = (accountId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskData: CreateTaskRequest) =>
      TasksService.createTask(accountId, taskData),
    onSuccess: (newTask: Task) => {
      // Invalidate and refetch tasks list
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });

      // Optimistically update the cache
      queryClient.setQueryData(taskKeys.detail(accountId, newTask.id), newTask);

      toast.success('Task created successfully!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Failed to create task';
      toast.error(message);
    },
  });
};

// Hook for updating tasks
export const useUpdateTask = (accountId: string, taskId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskData: UpdateTaskRequest) =>
      TasksService.updateTask(accountId, taskId, taskData),
    onSuccess: (updatedTask: Task) => {
      // Update the single task cache
      queryClient.setQueryData(taskKeys.detail(accountId, taskId), updatedTask);

      // Invalidate tasks lists to reflect changes
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });

      toast.success('Task updated successfully!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Failed to update task';
      toast.error(message);
    },
  });
};

// Hook for deleting tasks
export const useDeleteTask = (accountId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => TasksService.deleteTask(accountId, taskId),
    onSuccess: (_, taskId) => {
      // Remove task from cache
      queryClient.removeQueries({
        queryKey: taskKeys.detail(accountId, taskId),
      });

      // Invalidate tasks lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });

      toast.success('Task deleted successfully!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Failed to delete task';
      toast.error(message);
    },
  });
};
