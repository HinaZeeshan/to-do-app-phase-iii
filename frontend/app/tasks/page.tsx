'use client';

import { useState } from 'react';
import { useTasks } from '../../hooks/useTasks';
import { useAuth } from '../../hooks/useAuth';
import TaskList from '../../components/tasks/TaskList';
import TaskForm from '../../components/tasks/TaskForm';
import EmptyState from '../../components/tasks/EmptyState';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';

export default function TasksPage() {
  const { tasks, loading, error, createTask, updateTask, deleteTask, toggleTaskCompletion, clearError } = useTasks();
  const { user } = useAuth();
  const [showForm, setShowForm] = useState(false);

  const handleCreateTask = async (title: string, description?: string) => {
    await createTask(title, description);
    setShowForm(false);
  };

  return (
    <div className="max-w-4xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
      <div className="px-0 sm:px-4 py-6 sm:px-0">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">My Tasks</h1>
          <Button onClick={() => setShowForm(!showForm)} variant="primary" className="w-full sm:w-auto">
            {showForm ? 'Cancel' : 'Add Task'}
          </Button>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
                <div className="mt-2 text-sm text-red-700">
                  <button
                    onClick={clearError}
                    className="font-medium text-red-700 hover:text-red-600 underline"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showForm && (
          <div className="mb-6">
            <TaskForm onSubmit={handleCreateTask} onCancel={() => setShowForm(false)} />
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        ) : tasks.length === 0 ? (
          <EmptyState onCreateTask={() => setShowForm(true)} />
        ) : (
          <TaskList
            tasks={tasks}
            onUpdate={updateTask}
            onDelete={deleteTask}
            onToggle={toggleTaskCompletion}
          />
        )}
      </div>
    </div>
  );
}