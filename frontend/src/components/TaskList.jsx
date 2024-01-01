import React from 'react';

const TaskList = ({ tasks, onDeleteTask, searchResults, isSearchMode }) => {
  const displayTasks = isSearchMode ? searchResults : tasks;

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'HIGH': return 'task-priority-high';
      case 'MEDIUM': return 'task-priority-medium';
      case 'LOW': return 'task-priority-low';
      default: return '';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'TASK':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 11l3 3L22 4"></path>
            <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
          </svg>
        );
      case 'REMINDER':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        );
      case 'NOTE':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        );
      default:
        return null;
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'HIGH':
        return (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        );
      case 'MEDIUM':
        return (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="1.5">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
        );
      case 'LOW':
        return (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getDateIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
      <line x1="16" y1="2" x2="16" y2="6"></line>
      <line x1="8" y1="2" x2="8" y2="6"></line>
      <line x1="3" y1="10" x2="21" y2="10"></line>
    </svg>
  );

  const formatDate = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    }

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const isOverdue = (dueDate) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date().setHours(0, 0, 0, 0);
  };

  const isHighPriority = (priority) => {
    return priority === 'HIGH';
  };

  const isDueSoon = (dueDate) => {
    if (!dueDate) return false;
    const due = new Date(dueDate);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return due.toDateString() === today.toDateString() || due.toDateString() === tomorrow.toDateString();
  };

  if (!displayTasks || displayTasks.length === 0) {
    return (
      <div className="empty-state">
        <p>
          {isSearchMode
            ? 'No results found. Try different keywords.'
            : 'No items yet. Add your first task above.'
          }
        </p>
      </div>
    );
  }

  return (
    <div className="task-list">
      {displayTasks.map((task) => (
        <div key={task.id} data-category={task.category} className={`task-card ${isHighPriority(task.priority) ? 'high-priority' : ''} ${isOverdue(task.due_date) ? 'overdue-task' : ''} ${isDueSoon(task.due_date) ? 'due-soon' : ''} ${task.category === 'NOTE' ? 'note-card' : ''}`}>
          <div className="task-header">
            <div className="task-category-badge">
              {getCategoryIcon(task.category)}
              <span>{task.category}</span>
            </div>
            <div className="task-header-right">
              <div className="priority-indicator-wrapper">
                {getPriorityIcon(task.priority)}
                <span className={`task-priority ${getPriorityClass(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
              {isHighPriority(task.priority) && (
                <span className="priority-indicator high">HIGH</span>
              )}
              {isOverdue(task.due_date) && (
                <span className="priority-indicator overdue">OVERDUE</span>
              )}
              {isDueSoon(task.due_date) && !isOverdue(task.due_date) && (
                <span className="priority-indicator due-soon">DUE SOON</span>
              )}
            </div>
          </div>

          <div className="task-content">
            <p className="task-text">{task.content}</p>
          </div>

          <div className="task-footer">
            <div className="task-meta">
              {task.due_date && (
                <div className={`task-date-badge ${isOverdue(task.due_date) ? 'overdue' : isDueSoon(task.due_date) ? 'due-soon' : ''}`}>
                  <span className="date-icon">{getDateIcon()}</span>
                  <span>
                    {isOverdue(task.due_date) ? 'Overdue: ' : isDueSoon(task.due_date) ? 'Due Soon: ' : 'Due: '}
                    {formatDate(task.due_date)}
                  </span>
                </div>
              )}
              {task.created_at && (
                <span className="task-created-date">
                  <span className="bullet-separator">•</span>
                  Created {formatDate(task.created_at)}
                </span>
              )}
              {isSearchMode && task.similarity && (
                <div className="match-score-badge">
                  <span>Match: {Math.round(task.similarity * 100)}%</span>
                </div>
              )}
            </div>

            {!isSearchMode && (
              <button
                className="btn-delete"
                onClick={() => onDeleteTask(task.id)}
                title="Delete task"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TaskList;
