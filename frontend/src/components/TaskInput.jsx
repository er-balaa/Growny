import React, { useState } from 'react';

const TaskInput = ({ onAddTask, onSearch, mode, setMode }) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    try {
      if (mode === 'search') {
        await onSearch(input);
      } else {
        await onAddTask(input);
        setInput('');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="input-container">
      <div className="mode-toggle">
        <button
          className={`mode-btn ${mode === 'add' ? 'active' : ''}`}
          onClick={() => setMode('add')}
        >
          Add
        </button>
        <button
          className={`mode-btn ${mode === 'search' ? 'active' : ''}`}
          onClick={() => setMode('search')}
        >
          Search
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            mode === 'search'
              ? 'Search your tasks...'
              : 'What do you need to do?'
          }
          className="input-field"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary"
          style={{ flexShrink: 0 }}
        >
          {loading ? '...' : mode === 'search' ? 'Search' : 'Add'}
        </button>
      </form>
    </div>
  );
};

export default TaskInput;
