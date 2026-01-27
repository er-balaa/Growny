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
    // Return null to remove all category icons
    return null;
  };

  const getPriorityIcon = (priority) => {
    // Return null to remove all priority icons
    return null;
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
