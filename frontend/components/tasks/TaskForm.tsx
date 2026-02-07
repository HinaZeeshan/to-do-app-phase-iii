import React, { useState } from 'react';
import Input from '../ui/Input';
import Button from '../ui/Button';

interface TaskFormProps {
  onSubmit: (title: string, description?: string) => void;
  onCancel: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ onSubmit, onCancel }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onSubmit(title, description.trim() || undefined);
      setTitle('');
      setDescription('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        name="title"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
        label="Title"
        required={true}
      />
      <Input
        name="description"
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Task description (optional)"
        label="Description"
      />
      <div className="flex space-x-2">
        <Button type="submit" variant="primary">Create Task</Button>
        <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
};

export default TaskForm;