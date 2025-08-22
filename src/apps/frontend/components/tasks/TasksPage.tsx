import React, { useState, useMemo } from 'react';
import { useTasks, useDeleteTask } from '../../hooks/useTasks';
import { TaskCreationForm } from './TaskCreationForm';
import { TaskComments } from './TaskComments';
import { Task } from '../../services/tasks.service';
import './Tasks.css';

interface TasksPageProps {
  accountId: string;
}

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  selectedTask: Task | null;
  onTaskSelect: (task: Task) => void;
  onTaskDelete: (taskId: string) => void;
  isDeleting: boolean;
}

interface TaskFiltersProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
}

interface TaskFilters {
  search: string;
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  filters,
  onFiltersChange,
}) => {
  return (
    <div className="task-filters">
      <div className="filter-group">
        <input
          type="text"
          placeholder="Search tasks..."
          value={filters.search}
          onChange={(e) =>
            onFiltersChange({ ...filters, search: e.target.value })
          }
          className="search-input"
        />
      </div>
    </div>
  );
};

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  isLoading,
  selectedTask,
  onTaskSelect,
  onTaskDelete,
  isDeleting,
}) => {
  if (isLoading) {
    return (
      <div className="task-list-loading">
        <div className="loading-state">
          <span className="spinner"></span>
          Loading tasks...
        </div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="task-list-empty">
        <div className="empty-state">
          <h3>No tasks found</h3>
          <p>Create your first task to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="task-list">
      {tasks.map((task) => (
        <div
          key={task.id}
          className={`task-item ${selectedTask?.id === task.id ? 'selected' : ''}`}
          onClick={() => onTaskSelect(task)}
        >
          <div className="task-item-header">
            <h3 className="task-item-title">{task.title}</h3>
          </div>

          {task.description && (
            <p className="task-item-description">{task.description}</p>
          )}

          <div className="task-item-footer">
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (
                  window.confirm('Are you sure you want to delete this task?')
                ) {
                  onTaskDelete(task.id);
                }
              }}
              className="task-delete-btn"
              disabled={isDeleting}
              title="Delete task"
            >
              {isDeleting ? '...' : '🗑️'}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export const TasksPage: React.FC<TasksPageProps> = ({ accountId }) => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [filters, setFilters] = useState<TaskFilters>({
    search: '',
  });

  const { data: tasksData, isLoading, error } = useTasks(accountId);

  const deleteTaskMutation = useDeleteTask(accountId);

  // Filter tasks based on search
  const filteredTasks = useMemo(() => {
    if (!tasksData?.items) return [];

    let filtered = tasksData.items;

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(
        (task) =>
          task.title.toLowerCase().includes(searchLower) ||
          task.description?.toLowerCase().includes(searchLower),
      );
    }

    return filtered;
  }, [tasksData?.items, filters.search]);

  const handleTaskDelete = async (taskId: string) => {
    if (selectedTask?.id === taskId) {
      setSelectedTask(null);
    }
    await deleteTaskMutation.mutateAsync(taskId);
  };

  const handleTaskCreated = () => {
    // Optionally select the newly created task
    // This would require returning the created task from the mutation
  };

  if (error) {
    return (
      <div className="tasks-page error">
        <div className="error-state">
          <h3>Failed to load tasks</h3>
          <p>Please refresh the page and try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tasks-page">
      <div className="tasks-sidebar">
        <div className="sidebar-header">
          <h1>My Tasks</h1>
          <p className="tasks-count">
            {filteredTasks.length} of {tasksData?.items?.length || 0} tasks
          </p>
        </div>

        <TaskCreationForm accountId={accountId} onSuccess={handleTaskCreated} />

        <TaskFilters filters={filters} onFiltersChange={setFilters} />

        <TaskList
          tasks={filteredTasks}
          isLoading={isLoading}
          selectedTask={selectedTask}
          onTaskSelect={setSelectedTask}
          onTaskDelete={handleTaskDelete}
          isDeleting={deleteTaskMutation.isPending}
        />
      </div>

      <div className="tasks-main">
        {selectedTask ? (
          <TaskComments task={selectedTask} />
        ) : (
          <div className="no-task-selected">
            <div className="empty-state">
              <h2>Select a task</h2>
              <p>
                Choose a task from the sidebar to view its details and comments
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
