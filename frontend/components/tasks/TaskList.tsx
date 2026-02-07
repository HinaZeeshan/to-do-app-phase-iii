import React, { memo } from 'react';
import { TodoItem } from '../../../frontend/types';
import TaskCard from './TaskCard';

interface TaskListProps {
  tasks: TodoItem[];
  onUpdate: (id: string, updates: Partial<TodoItem>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onToggle: (id: string) => Promise<void>;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onUpdate, onDelete, onToggle }) => {
  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onDelete={onDelete}
          onToggle={onToggle}
        />
      ))}
    </div>
  );
};

export default memo(TaskList);