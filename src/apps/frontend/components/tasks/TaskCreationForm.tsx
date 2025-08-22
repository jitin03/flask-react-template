import React, { useState } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useCreateTask } from '../../hooks/useTasks';
import { CreateTaskRequest } from '../../services/tasks.service';

interface TaskCreationFormProps {
  accountId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
  className?: string;
}

const validationSchema = Yup.object({
  title: Yup.string()
    .required('Title is required')
    .min(3, 'Title must be at least 3 characters')
    .max(100, 'Title must be less than 100 characters'),
  description: Yup.string().max(
    500,
    'Description must be less than 500 characters',
  ),
});

export const TaskCreationForm: React.FC<TaskCreationFormProps> = ({
  accountId,
  onSuccess,
  onCancel,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const createTaskMutation = useCreateTask(accountId);

  const formik = useFormik<CreateTaskRequest>({
    initialValues: {
      title: '',
      description: '',
    },
    validationSchema,
    onSubmit: async (values, { resetForm }) => {
      try {
        const taskData: CreateTaskRequest = {
          title: values.title,
          description: values.description || undefined,
        };

        await createTaskMutation.mutateAsync(taskData);
        resetForm();
        setIsExpanded(false);
        onSuccess?.();
      } catch (error) {
        // Error handling is done in the mutation hook
      }
    },
  });

  const handleCancel = () => {
    formik.resetForm();
    setIsExpanded(false);
    onCancel?.();
  };

  return (
    <div className={`task-creation-form ${className}`}>
      {!isExpanded ? (
        <button
          onClick={() => setIsExpanded(true)}
          className="task-creation-trigger"
          type="button"
        >
          <span className="plus-icon">+</span>
          Add a new task...
        </button>
      ) : (
        <form onSubmit={formik.handleSubmit} className="task-form-expanded">
          <div className="form-group">
            <input
              type="text"
              id="title"
              name="title"
              placeholder="Task title *"
              value={formik.values.title}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              className={`form-input ${formik.touched.title && formik.errors.title ? 'error' : ''}`}
              disabled={createTaskMutation.isPending}
              autoFocus
            />
            {formik.touched.title && formik.errors.title && (
              <div className="error-message">{formik.errors.title}</div>
            )}
          </div>

          <div className="form-group">
            <textarea
              id="description"
              name="description"
              placeholder="Description (optional)"
              value={formik.values.description}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              className={`form-textarea ${formik.touched.description && formik.errors.description ? 'error' : ''}`}
              disabled={createTaskMutation.isPending}
              rows={3}
            />
            {formik.touched.description && formik.errors.description && (
              <div className="error-message">{formik.errors.description}</div>
            )}
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={
                createTaskMutation.isPending || !formik.values.title.trim()
              }
            >
              {createTaskMutation.isPending ? (
                <>
                  <span className="spinner"></span>
                  Creating...
                </>
              ) : (
                'Create Task'
              )}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="btn-secondary"
              disabled={createTaskMutation.isPending}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
