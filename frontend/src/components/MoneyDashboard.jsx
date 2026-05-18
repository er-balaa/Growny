import React from 'react';

const MoneyDashboard = ({ transactions = [], onDeleteTransaction }) => {
  // Simple calculations for overview
  const totalIncome = transactions
    .filter(t => t.type === 'INCOME')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
  const totalExpense = transactions
    .filter(t => t.type === 'EXPENSE')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
  const netWorth = totalIncome - totalExpense;

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    });
  };

  if (!transactions || transactions.length === 0) {
    return (
      <div className="money-dashboard">
        <div className="empty-state">
          <p>No transactions yet. Ask Growny to log an expense or income!</p>
          <p className="hint">Try: "I spent $50 on groceries today"</p>
        </div>
      </div>
    );
  }

  return (
    <div className="money-dashboard">
      <div className="finance-overview">
        <div className="finance-card net-worth">
          <span className="card-label">Net Balance</span>
          <h2 className="card-value">₹{netWorth.toFixed(2)}</h2>
        </div>
        <div className="finance-card income">
          <span className="card-label">Total Income</span>
          <h2 className="card-value text-success">₹{totalIncome.toFixed(2)}</h2>
        </div>
        <div className="finance-card expense">
          <span className="card-label">Total Expense</span>
          <h2 className="card-value text-danger">₹{totalExpense.toFixed(2)}</h2>
        </div>
      </div>

      <div className="transactions-section">
        <h3>Recent Transactions</h3>
        <div className="transactions-list">
          {transactions.map(tx => (
            <div key={tx.id} className={`transaction-item ${tx.type.toLowerCase()}`}>
              <div className="tx-icon">
                {tx.type === 'INCOME' ? '↓' : '↑'}
              </div>
              <div className="tx-details">
                <div className="tx-header">
                  <span className="tx-desc">{tx.description}</span>
                  <span className={`tx-amount ${tx.type.toLowerCase()}`}>
                    {tx.type === 'INCOME' ? '+' : '-'}₹{tx.amount.toFixed(2)}
                  </span>
                </div>
                <div className="tx-meta">
                  <span className="tx-category">{tx.category || 'General'}</span>
                  <span className="tx-date">{formatDate(tx.date)}</span>
                </div>
              </div>
              <button 
                className="task-delete-btn" 
                onClick={() => onDeleteTransaction(tx.id)}
                title="Delete"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MoneyDashboard;
