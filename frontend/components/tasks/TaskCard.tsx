import React, { useState } from 'react';
import { TodoItem } from '../../../frontend/types';
import Button from '../ui/Button';
import Input from '../ui/Input';

interface TaskCardProps {
  task: TodoItem;
  onUpdate: (id: string, updates: Partial<TodoItem>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onToggle: (id: string) => Promise<void>;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onUpdate, onDelete, onToggle }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');

  const handleToggle = async () => {
    await onToggle(task.id);
  };

  const handleSave = async () => {
    await onUpdate(task.id, { title, description: description || null });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setTitle(task.title);
    setDescription(task.description || '');
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await onDelete(task.id);
    }
  };

  return (
    <div className={`border rounded-lg shadow-sm p-4 ${task.completed ? 'bg-green-50' : 'bg-white'}`}>
      {isEditing ? (
        <div className="space-y-4">
          <Input
            name="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            label="Title"
            required={true}
          />
          <Input
            name="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            label="Description"
          />
          <div className="flex flex-col sm:flex-row sm:space-x-2 space-y-2 sm:space-y-0">
            <Button onClick={handleSave} variant="primary" className="w-full sm:w-auto">Save</Button>
            <Button onClick={handleCancel} variant="secondary" className="w-full sm:w-auto">Cancel</Button>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex flex-col sm:flex-row sm:items-start">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={handleToggle}
              className="h-4 w-4 text-blue-600 rounded mt-1 sm:mt-0 self-start sm:self-center"
            />
            <div className="ml-0 sm:ml-3 flex-1 w-full">
              <h3 className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className={`mt-1 ${task.completed ? 'line-through text-gray-500' : 'text-gray-600'}`}>
                  {task.description}
                </p>
              )}
              <p className="mt-2 text-xs text-gray-500">
                Created: {new Date(task.createdAt).toLocaleDateString()} |
                Updated: {new Date(task.updatedAt).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-col sm:flex-row sm:space-x-2 space-y-2 sm:space-y-0">
            <Button onClick={() => setIsEditing(true)} variant="secondary" className="w-full sm:w-auto">Edit</Button>
            <Button onClick={handleDelete} variant="danger" className="w-full sm:w-auto">Delete</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default React.memo(TaskCard);