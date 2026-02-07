import { useState, useEffect } from 'react';
import { todoApi } from '../lib/api';
import { TodoItem } from '../types';

interface TasksState {
  tasks: TodoItem[];
  loading: boolean;
  error: string | null;
  creating: boolean;
  updating: boolean;
  deleting: boolean;
}

export const useTasks = () => {
  const [state, setState] = useState<TasksState>({
    tasks: [],
    loading: false,
    error: null,
    creating: false,
    updating: false,
    deleting: false,
  });

  // Fetch all tasks
  const fetchTasks = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await todoApi.getAll();

      setState(prev => ({
        ...prev,
        tasks: response.data || [],
        loading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tasks';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  };

  // Create a new task
  const createTask = async (title: string, description?: string) => {
    setState(prev => ({ ...prev, creating: true, error: null }));

    try {
      const response = await todoApi.create({ title, description, completed: false });

      const newTask = response.data;
      if (newTask) {
        setState(prev => ({
          ...prev,
          tasks: [...prev.tasks, newTask],
          creating: false,
        }));
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create task';
      setState(prev => ({
        ...prev,
        creating: false,
        error: errorMessage,
      }));
    }
  };

  // Update a task
  const updateTask = async (id: string, updates: Partial<TodoItem>) => {
    setState(prev => ({ ...prev, updating: true, error: null }));

    try {
      const response = await todoApi.update(id, updates);

      const updatedTask = response.data;
      if (updatedTask) {
        setState(prev => ({
          ...prev,
          tasks: prev.tasks.map(task =>
            task.id === id ? updatedTask : task
          ),
          updating: false,
        }));
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      setState(prev => ({
        ...prev,
        updating: false,
        error: errorMessage,
      }));
    }
  };

  // Toggle task completion
  const toggleTaskCompletion = async (id: string) => {
    setState(prev => ({ ...prev, updating: true, error: null }));

    try {
      const response = await todoApi.toggleCompletion(id);

      const updatedTask = response.data;
      if (updatedTask) {
        setState(prev => ({
          ...prev,
          tasks: prev.tasks.map(task =>
            task.id === id ? updatedTask : task
          ),
          updating: false,
        }));
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to toggle task completion';
      setState(prev => ({
        ...prev,
        updating: false,
        error: errorMessage,
      }));
    }
  };

  // Delete a task
  const deleteTask = async (id: string) => {
    setState(prev => ({ ...prev, deleting: true, error: null }));

    try {
      await todoApi.delete(id);

      setState(prev => ({
        ...prev,
        tasks: prev.tasks.filter(task => task.id !== id),
        deleting: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete task';
      setState(prev => ({
        ...prev,
        deleting: false,
        error: errorMessage,
      }));
    }
  };

  // Load tasks on mount
  useEffect(() => {
    fetchTasks();

    // Listen for custom "task-updated" event (e.g., from chatbot)
    const handleTaskUpdate = () => {
      fetchTasks();
    };

    window.addEventListener('task-updated', handleTaskUpdate);
    return () => {
      window.removeEventListener('task-updated', handleTaskUpdate);
    };
  }, []);

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  return {
    ...state,
    fetchTasks,
    createTask,
    updateTask,
    toggleTaskCompletion,
    deleteTask,
    clearError,
  };
};