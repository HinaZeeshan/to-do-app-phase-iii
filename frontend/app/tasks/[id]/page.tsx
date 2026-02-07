'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useTasks } from '../../../hooks/useTasks';
import { TodoItem } from '../../../types';
import TaskCard from '../../../components/tasks/TaskCard';
import LoadingSpinner from '../../../components/ui/LoadingSpinner';

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { tasks, loading, error } = useTasks();
  const [task, setTask] = useState<TodoItem | undefined>(undefined);

  useEffect(() => {
    if (tasks.length > 0) {
      const foundTask = tasks.find(t => t.id === id);
      setTask(foundTask);
    }
  }, [tasks, id]);

  if (loading && !task) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4 m-4">
        <div className="text-sm text-red-700">{error}</div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="p-4">
        <div className="rounded-md bg-yellow-50 p-4">
          <div className="text-sm text-yellow-700">Task not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Task Details</h1>
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <TaskCard task={task} />
        </div>
      </div>
    </div>
  );
}