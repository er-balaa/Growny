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
            className={`task-item-minimal ${overdue ? 'overdue' : ''} ${dueSoon && !overdue ? 'due-soon' : ''} ${task._pending ? 'task-pending' : ''}`}
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
                    <span className={`task-badge date ${overdue ? 'overdue' : dueSoon ? 'due-soon' : ''}`} style={{ display: 'flex', alignItems: 'center' }}>
                      {overdue ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '4px'}}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                      ) : dueSoon ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '4px'}}><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '4px'}}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                      )}
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
