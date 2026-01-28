import React from 'react';

const TaskList = ({ tasks, onDeleteTask, searchResults, isSearchMode }) => {
  const displayTasks = isSearchMode ? searchResults : tasks;

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

  const isDueSoon = (dueDate) => {
    if (!dueDate) return false;
    const due = new Date(dueDate);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return due.toDateString() === today.toDateString() || due.toDateString() === tomorrow.toDateString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return '#ef4444';
      case 'MEDIUM': return '#f59e0b';
      case 'LOW': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'TASK': return '#3b82f6';
      case 'REMINDER': return '#f59e0b';
      case 'NOTE': return '#10b981';
      default: return '#6b7280';
    }
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
    <div className="task-list-minimal">
      {displayTasks.map((task) => {
        const priorityColor = getPriorityColor(task.priority);
        const categoryColor = getCategoryColor(task.category);
        const overdue = isOverdue(task.due_date);
        const dueSoon = isDueSoon(task.due_date);

        return (
          <div
            key={task.id}
            className={`task-item-minimal ${overdue ? 'overdue' : ''} ${dueSoon && !overdue ? 'due-soon' : ''}`}
            style={{ '--priority-color': priorityColor, '--category-color': categoryColor }}
          >
            {/* Priority indicator line */}
            <div className="task-priority-line" style={{ backgroundColor: priorityColor }}></div>

            <div className="task-main">
              <div className="task-content-minimal">
                <p className="task-text-minimal">{task.content}</p>
              </div>

              <div className="task-info-row">
                <div className="task-badges">
                  <span className="task-badge category" style={{ color: categoryColor, borderColor: `${categoryColor}30`, backgroundColor: `${categoryColor}10` }}>
                    {task.category}
                  </span>
                  <span className="task-badge priority" style={{ color: priorityColor, borderColor: `${priorityColor}30`, backgroundColor: `${priorityColor}10` }}>
                    {task.priority}
                  </span>
                  {task.due_date && (
                    <span className={`task-badge date ${overdue ? 'overdue' : dueSoon ? 'due-soon' : ''}`}>
                      {overdue ? '⚠ ' : dueSoon ? '⏰ ' : '📅 '}
                      {formatDate(task.due_date)}
                    </span>
                  )}
                  {isSearchMode && task.similarity && (
                    <span className="task-badge match">
                      {Math.round(task.similarity * 100)}% match
                    </span>
                  )}
                </div>

                {!isSearchMode && (
                  <button
                    className="task-delete-btn"
                    onClick={() => onDeleteTask(task.id)}
                    title="Delete"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default TaskList;
