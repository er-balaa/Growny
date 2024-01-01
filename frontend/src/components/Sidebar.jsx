import React from 'react';

const Sidebar = ({
    activeView,
    setActiveView,
    taskCounts,
    user,
    onSignOut,
    onNewChat,
    Avatar,
    IconPlus,
    IconSearch,
    IconImportant,
    IconBell,
    IconNote,
    IconTask
}) => {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <span className="sidebar-logo">Growny<span>AI</span></span>
            </div>

            {/* New Chat */}
            <button className="new-chat-btn" onClick={onNewChat}>
                <span className="new-chat-icon">{IconPlus && <IconPlus />}</span>
                New chat
            </button>

            {/* Search */}
            <button
                className={`sidebar-item ${activeView === 'search' ? 'active' : ''}`}
                onClick={() => setActiveView('search')}
            >
                <span className="sidebar-icon">{IconSearch && <IconSearch />}</span>
                Search chats
            </button>

            <div className="sidebar-divider"></div>

            {/* Categories */}
            <div className="sidebar-section">
                <button
                    className={`sidebar-item ${activeView === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveView('all')}
                >
                    <span className="sidebar-icon">{IconImportant && <IconImportant />}</span>
                    Important
                    {taskCounts.all > 0 && <span className="sidebar-count">{taskCounts.all}</span>}
                </button>

                <button
                    className={`sidebar-item ${activeView === 'notes' ? 'active' : ''}`}
                    onClick={() => setActiveView('notes')}
                >
                    <span className="sidebar-icon">{IconNote && <IconNote />}</span>
                    Notes
                    {taskCounts.notes > 0 && <span className="sidebar-count">{taskCounts.notes}</span>}
                </button>

                <button
                    className={`sidebar-item ${activeView === 'reminders' ? 'active' : ''}`}
                    onClick={() => setActiveView('reminders')}
                >
                    <span className="sidebar-icon">{IconBell && <IconBell />}</span>
                    Reminders
                    {taskCounts.reminders > 0 && <span className="sidebar-count">{taskCounts.reminders}</span>}
                </button>

                <button
                    className={`sidebar-item ${activeView === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveView('tasks')}
                >
                    <span className="sidebar-icon">{IconTask && <IconTask />}</span>
                    Tasks
                    {taskCounts.tasks > 0 && <span className="sidebar-count">{taskCounts.tasks}</span>}
                </button>
            </div>

            {/* User */}
            {user && (
                <div className="sidebar-user">
                    {Avatar && <Avatar size="medium" />}
                    <span className="user-name">{user.displayName?.split(' ')[0]}</span>
                    <button className="btn-secondary" onClick={onSignOut}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line>
                        </svg>
                    </button>
                </div>
            )}
        </aside>
    );
};

export default Sidebar;
