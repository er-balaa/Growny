import React, { useState, useEffect } from 'react';
import Auth from './components/Auth';
import Sidebar from './components/Sidebar';
import TaskList from './components/TaskList';
import { taskAPI } from './services/api';
import { signOut } from 'firebase/auth';
import { auth } from './firebase';

// --- Professional Icons (SVG) ---
const IconPlus = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const IconSearch = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
  </svg>
);

const IconImportant = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const IconBell = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"></path>
    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
  </svg>
);

const IconNote = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <line x1="10" y1="9" x2="8" y2="9"></line>
  </svg>
);

const IconTask = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 11l3 3L22 4"></path>
    <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
  </svg>
);

function App() {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [activeView, setActiveView] = useState('chat');
  const [chatInput, setChatInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('user');
      const storedToken = localStorage.getItem('authToken');

      if (storedUser && storedToken) {
        const user = JSON.parse(storedUser);
        setUser(user);
        loadTasks(true);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error loading stored user data:', error);
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showProfileDropdown && !e.target.closest('.mobile-profile-wrapper')) {
        setShowProfileDropdown(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showProfileDropdown]);

  const loadTasks = async (eager = false) => {
    try {
      // Set loading state for eager loading
      if (eager) {
        setTasksLoading(true);
      }
      
      const tasksData = await taskAPI.getTasks();
      setTasks(tasksData);
    } catch (error) {
      console.error('Error loading tasks:', error);
      console.error('Error details:', error.response?.data || error.message);
    } finally {
      setLoading(false);
      setTasksLoading(false);
    }
  };

  const handleAuthStateChange = (userData) => {
    try {
      if (userData) {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('authToken', userData.token);
        loadTasks();
      } else {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('authToken');
        setTasks([]);
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Error in handleAuthStateChange:', error);
      setUser(null);
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');
      setTasks([]);
      setSearchResults([]);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      handleAuthStateChange(null);
      setShowProfileDropdown(false);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      if (activeView === 'search') {
        const results = await taskAPI.searchTasks(chatInput);
        setSearchResults(results);
      } else {
        const result = await taskAPI.createTask(chatInput);
        if (result.success) {
          await loadTasks();
          setChatInput('');
          setActiveView('all');
        }
      }
    } catch (error) {
      console.error('Error:', error);
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await taskAPI.deleteTask(taskId);
      await loadTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleNewChat = () => {
    setActiveView('chat');
    setChatInput('');
  };

  const getFilteredTasks = () => {
    let filtered = tasks;
    if (activeView === 'search') {
      filtered = searchResults;
    } else {
      switch (activeView) {
        case 'tasks':
          filtered = tasks.filter(t => t.category === 'TASK');
          break;
        case 'reminders':
          filtered = tasks.filter(t => t.category === 'REMINDER');
          break;
        case 'notes':
          filtered = tasks.filter(t => t.category === 'NOTE');
          break;
        case 'all':
        default:
          // Important view: Show high priority first, then by due date
          filtered = tasks.filter(t => t.category !== 'NOTE');
          break;
      }
    }

    // Enhanced sorting logic for better visibility
    return [...filtered].sort((a, b) => {
      // Priority sorting: HIGH > MEDIUM > LOW
      const priorityOrder = { 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 };
      const priorityDiff = (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
      if (priorityDiff !== 0) return priorityDiff;

      // Due date sorting: overdue > today > tomorrow > future
      const today = new Date().setHours(0, 0, 0, 0);
      const dateA = a.due_date ? new Date(a.due_date).getTime() : null;
      const dateB = b.due_date ? new Date(b.due_date).getTime() : null;

      if (dateA && dateB) {
        // Both have due dates
        const overdueA = dateA < today;
        const overdueB = dateB < today;
        if (overdueA !== overdueB) return overdueA ? -1 : 1; // Overdue first
        return dateA - dateB; // Earlier due date first
      } else if (dateA) {
        return -1; // A has due date, show first
      } else if (dateB) {
        return 1; // B has due date, show first
      }

      // Created date sorting (newest first)
      const createdA = a.created_at ? new Date(a.created_at).getTime() : 0;
      const createdB = b.created_at ? new Date(b.created_at).getTime() : 0;
      return createdB - createdA;
    });
  };

  const getTaskCounts = () => ({
    all: tasks.filter(t => t.category !== 'NOTE').length,
    tasks: tasks.filter(t => t.category === 'TASK').length,
    reminders: tasks.filter(t => t.category === 'REMINDER').length,
    notes: tasks.filter(t => t.category === 'NOTE').length,
  });

  const getUserInitial = () => {
    if (user?.displayName) return user.displayName.charAt(0).toUpperCase();
    if (user?.email) return user.email.charAt(0).toUpperCase();
    return '?';
  };

  const Avatar = ({ size = 'medium', className = '' }) => {
    const [imgError, setImgError] = useState(false);

    const sizeClasses = {
      small: 'mobile-avatar',
      medium: 'avatar',
      large: 'dropdown-avatar'
    };
    const fallbackClasses = {
      small: 'mobile-avatar-fallback',
      medium: 'avatar-fallback',
      large: 'dropdown-avatar-fallback'
    };

    if (user?.photoURL && !imgError) {
      return (
        <img
          className={`${sizeClasses[size]} ${className}`}
          src={user.photoURL}
          alt=""
          onError={() => setImgError(true)}
        />
      );
    }
    return <div className={`${fallbackClasses[size]} ${className}`}>{getUserInitial()}</div>;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="auth-container">
        <h1 className="auth-title">Growny<span>AI</span></h1>
        <p className="auth-subtitle">Your intelligent personal assistant</p>
        <Auth user={user} onAuthStateChange={handleAuthStateChange} />
      </div>
    );
  }

  const filteredTasks = getFilteredTasks();
  const isListView = activeView !== 'chat';

  return (
    <div className="app-container">
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        taskCounts={getTaskCounts()}
        user={user}
        onSignOut={handleSignOut}
        onNewChat={handleNewChat}
        Avatar={Avatar}
        IconPlus={IconPlus}
        IconSearch={IconSearch}
        IconImportant={IconImportant}
        IconBell={IconBell}
        IconNote={IconNote}
        IconTask={IconTask}
      />

      <header className="mobile-header">
        <div className="mobile-header-content">
          <div className="mobile-logo-group">
            <span className="mobile-logo">Growny<span>AI</span></span>
          </div>

          <div className="mobile-user-info">
            <span className="mobile-username">{user.displayName?.split(' ')[0]}</span>
            <div className="mobile-profile-wrapper">
              <button
                className="mobile-profile-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowProfileDropdown(!showProfileDropdown);
                }}
              >
                <Avatar size="small" />
              </button>

              {showProfileDropdown && (
                <div className="profile-dropdown">
                  <div className="dropdown-header">
                    <Avatar size="large" />
                    <div className="dropdown-info">
                      <div className="dropdown-name">{user.displayName}</div>
                      <div className="dropdown-email">{user.email}</div>
                    </div>
                  </div>
                  <button className="dropdown-signout" onClick={handleSignOut}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                      <polyline points="7 17 12 12 17 7"></polyline>
                      <line x1="12" y1="22" x2="12" y2="17"></line>
                    </svg>
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="main-header">
          <div className="header-inner">
            <span className="model-selector">GrownyAI</span>
          </div>
        </div>

        {!isListView ? (
          <div className="chat-welcome">
            <h1 className="welcome-title">What's on your mind today?</h1>

            <div className="chat-input-container">
              <form onSubmit={handleChatSubmit}>
                <div className="chat-input-wrapper">
                  <span className="chat-input-icon"><IconPlus /></span>
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask anything"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    disabled={isSubmitting}
                  />
                  <button
                    type="submit"
                    className="chat-submit-btn"
                    disabled={!chatInput.trim() || isSubmitting}
                  >
                    Submit
                  </button>
                </div>
              </form>
            </div>
          </div>
        ) : (
          <div className="list-view">
            <div className="list-header">
              <h1 className="list-title">
                {activeView === 'search' ? 'Search Results' :
                  activeView === 'all' ? 'Important' :
                    activeView.charAt(0).toUpperCase() + activeView.slice(1)}
              </h1>
              <p className="list-count">{filteredTasks.length} items</p>
            </div>

            {activeView === 'search' && (
              <div style={{ marginBottom: '24px' }}>
                <form onSubmit={handleChatSubmit}>
                  <div className="chat-input-wrapper">
                    <span className="chat-input-icon"><IconSearch /></span>
                    <input
                      type="text"
                      className="chat-input"
                      placeholder="Search your tasks..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                    />
                    <button type="submit" className="chat-submit-btn">Send</button>
                  </div>
                </form>
              </div>
            )}

            {tasksLoading && (
              <div className="tasks-loading-container">
                <div className="spinner-small"></div>
                <span>Loading your tasks...</span>
              </div>
            )}

            <TaskList
              tasks={filteredTasks}
              searchResults={searchResults}
              onDeleteTask={handleDeleteTask}
              isSearchMode={activeView === 'search'}
            />
          </div>
        )}
      </main>

      <nav className="mobile-nav">
        <div className="mobile-nav-items">
          <button className={`mobile-nav-item ${activeView === 'chat' ? 'active' : ''}`} onClick={handleNewChat} title="Chat">
            <IconPlus />
          </button>
          <button className={`mobile-nav-item ${activeView === 'search' ? 'active' : ''}`} onClick={() => setActiveView('search')} title="Search">
            <IconSearch />
          </button>
          <button className={`mobile-nav-item ${activeView === 'all' ? 'active' : ''}`} onClick={() => setActiveView('all')} title="All">
            <IconImportant />
          </button>
          <button className={`mobile-nav-item ${activeView === 'reminders' ? 'active' : ''}`} onClick={() => setActiveView('reminders')} title="Reminders">
            <IconBell />
          </button>
          <button className={`mobile-nav-item ${activeView === 'notes' ? 'active' : ''}`} onClick={() => setActiveView('notes')} title="Notes">
            <IconNote />
          </button>
          <button className={`mobile-nav-item ${activeView === 'tasks' ? 'active' : ''}`} onClick={() => setActiveView('tasks')} title="Tasks">
            <IconTask />
          </button>
        </div>
      </nav>

      {activeView === 'chat' && (
        <div className="mobile-input-bar">
          <form onSubmit={handleChatSubmit}>
            <div className="mobile-input-row">
              <input
                type="text"
                placeholder="Ask anything..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit" className="mobile-submit">Send</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
