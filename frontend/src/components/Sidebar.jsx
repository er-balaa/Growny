import React from 'react';

const Sidebar = ({
    activeView,
    setActiveView,
    taskCounts,
    user,
    onSignOut,
    onNewChat,
    Avatar,
    isMobileOpen,
    onCloseMobile
}) => {
    return (
        <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
            <div className="sidebar-header">
                <span className="sidebar-logo">Growny<span>AI</span></span>
                {isMobileOpen && (
                    <button className="mobile-close-btn" onClick={onCloseMobile}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                )}
            </div>

            {/* Main Action */}
            <button className={`new-chat-btn ${activeView === 'chat' ? 'active' : ''}`} onClick={() => setActiveView('chat')}>
                <span className="new-chat-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                </span>
                Chat / Assistant
            </button>

            <div className="sidebar-divider"></div>

            <div className="sidebar-section">
                {/* WEALTH PILLAR */}
                <div className="sidebar-category-title">
                    WEALTH
                </div>
                <button
                    className={`sidebar-item ${activeView === 'money' ? 'active' : ''}`}
                    onClick={() => setActiveView('money')}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="3" y1="9" x2="21" y2="9"></line>
                        <line x1="9" y1="21" x2="9" y2="9"></line>
                    </svg>
                    Wealth Dashboard
                </button>

                {/* PRODUCTIVITY PILLAR */}
                <div className="sidebar-category-title sidebar-category-spacer">
                    PRODUCTIVITY
                </div>
                <button
                    className={`sidebar-item ${activeView === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveView('all')}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    Overview
                </button>
                <button
                    className={`sidebar-item ${activeView === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveView('tasks')}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 11l3 3L22 4"></path>
                        <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
                    </svg>
                    Tasks
                    {taskCounts.tasks > 0 && <span className="sidebar-count">{taskCounts.tasks}</span>}
                </button>
                <button
                    className={`sidebar-item ${activeView === 'reminders' ? 'active' : ''}`}
                    onClick={() => setActiveView('reminders')}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                    Reminders
                    {taskCounts.reminders > 0 && <span className="sidebar-count">{taskCounts.reminders}</span>}
                </button>
                <button
                    className={`sidebar-item ${activeView === 'notes' ? 'active' : ''}`}
                    onClick={() => setActiveView('notes')}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                    </svg>
                    Notes
                    {taskCounts.notes > 0 && <span className="sidebar-count">{taskCounts.notes}</span>}
                </button>

                {/* KNOWLEDGE PILLAR */}
                <div className="sidebar-category-title sidebar-category-spacer">
                    KNOWLEDGE
                </div>
                <button
                    className={`sidebar-item ${activeView === 'knowledge' ? 'active' : ''}`}
                    onClick={() => setActiveView('knowledge')}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                    </svg>
                    My Documents
                </button>
            </div>

            {/* User */}
            {user && (
                <div className="sidebar-user">
                    {Avatar && <Avatar size="medium" />}
                    <span className="user-name">{user.displayName?.split(' ')[0]}</span>
                    <button className="btn-secondary logout-btn" onClick={onSignOut}>
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
