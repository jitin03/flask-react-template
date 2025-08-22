import React from 'react';
import { useTasks } from '../../hooks/useTasks';
import { Task } from '../../services/tasks.service';
import './Dashboard.css';

interface DashboardPageProps {
  accountId: string;
}

interface TaskTableProps {
  tasks: Task[];
  isLoading: boolean;
}

const TaskTable: React.FC<TaskTableProps> = ({ tasks, isLoading }) => {
  if (isLoading) {
    return (
      <div className="table-loading">
        <div className="loading-spinner"></div>
        <p>Loading tasks...</p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <h3>No tasks found</h3>
        <p>
          Create your first task by navigating to the Tasks section in the
          sidebar.
        </p>
      </div>
    );
  }

  return (
    <div className="tasks-table-container">
      <table className="tasks-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td className="task-title">
                <div className="title-cell">{task.title}</div>
              </td>
              <td className="task-description">
                <div className="description-cell">
                  {task.description || '-'}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export const DashboardPage: React.FC<DashboardPageProps> = ({ accountId }) => {
  const { data: tasksData, isLoading, error } = useTasks(accountId);

  if (error) {
    return (
      <div className="dashboard-page error">
        <div className="error-state">
          <h3>Failed to load tasks</h3>
          <p>Please refresh the page and try again.</p>
        </div>
      </div>
    );
  }

  const tasks = tasksData?.items || [];

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="tasks-summary">
          {tasks.length} task{tasks.length !== 1 ? 's' : ''} total
        </p>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Recent Tasks</h2>
          </div>
          <TaskTable tasks={tasks} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};
