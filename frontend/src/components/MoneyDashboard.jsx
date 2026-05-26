import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, Sector } from 'recharts';

const renderActiveShape = (props) => {
  const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload } = props;
  return (
    <g style={{ outline: 'none', WebkitTapHighlightColor: 'transparent' }}>
      <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill} style={{ fontSize: '15px', fontWeight: '800', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
        {payload.name}
      </text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 8}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
        stroke="none"
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 12}
        outerRadius={outerRadius + 18}
        fill={fill}
        stroke="none"
      />
    </g>
  );
};

const MoneyDashboard = ({ transactions = [], onDeleteTransaction }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile(); // Check on mount
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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

  const expensesByCategory = transactions
    .filter(t => t.type === 'EXPENSE')
    .reduce((acc, t) => {
      const cat = (t.category && t.category.trim() !== '') ? t.category : 'General';
      acc[cat] = (acc[cat] || 0) + parseFloat(t.amount);
      return acc;
    }, {});

  const pieData = Object.entries(expensesByCategory)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  // Premium vibrant colors
  const COLORS = ['#FF4C29', '#FFB830', '#00B8A9', '#F83E4B', '#9D4EDD', '#FF6B6B', '#4D96FF', '#F9F871'];

  const displayedTransactions = selectedCategory 
    ? transactions.filter(t => t.type === 'EXPENSE' && ((t.category && t.category.trim() !== '' ? t.category : 'General') === selectedCategory))
    : transactions;

  const handlePieClick = (data, index) => {
    if (data && data.name) {
      if (selectedCategory === data.name) {
        setSelectedCategory(null);
        setActiveIndex(-1);
      } else {
        setSelectedCategory(data.name);
        setActiveIndex(index);
      }
    }
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

      {pieData.length > 0 && (
        <div className="transactions-section" style={{ marginTop: '24px', paddingBottom: '20px' }}>
          <h3>Expense Analysis <span style={{fontSize: '12px', fontWeight: 'normal', color: '#888'}}>(Tap slice to view details)</span></h3>
          <div style={{ width: '100%', height: isMobile ? 320 : 350, marginTop: '16px', background: '#1c1c1c', borderRadius: '12px', padding: isMobile ? '8px' : '16px', boxShadow: '0 8px 32px rgba(0,0,0,0.3)' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  activeIndex={activeIndex}
                  activeShape={renderActiveShape}
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={isMobile ? 85 : 110}
                  innerRadius={isMobile ? 55 : 75}
                  paddingAngle={6}
                  stroke="none"
                  labelLine={false}
                  label={activeIndex === -1 && !isMobile ? ({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%` : false}
                  onClick={handlePieClick}
                >
                  {pieData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[index % COLORS.length]} 
                      stroke="none"
                      style={{ outline: 'none', cursor: 'pointer', transition: 'all 0.3s ease', WebkitTapHighlightColor: 'transparent' }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => `₹${value.toFixed(2)}`}
                  contentStyle={{ backgroundColor: '#2a2a2a', borderColor: '#444', borderRadius: '12px', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
                  itemStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: isMobile ? '12px' : '14px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="transactions-section" style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>{selectedCategory ? `${selectedCategory} Transactions` : 'Recent Transactions'}</h3>
          {selectedCategory && (
            <button 
              onClick={() => { setSelectedCategory(null); setActiveIndex(-1); }}
              style={{ background: '#2a2a2a', color: '#fff', border: '1px solid #444', padding: '8px 14px', borderRadius: '8px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}
            >
              Clear Filter
            </button>
          )}
        </div>
        
        {selectedCategory && (
          <div style={{ margin: '16px 0', padding: '20px', background: 'linear-gradient(135deg, rgba(255,76,41,0.15), rgba(255,184,48,0.05))', borderRadius: '12px', border: '1px solid rgba(255,76,41,0.3)', animation: 'fadeIn 0.3s ease-in-out' }}>
            <p style={{ margin: 0, color: '#ccc', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>Total spent on {selectedCategory}</p>
            <h2 style={{ margin: '8px 0 0', color: '#FF4C29', fontSize: '28px', fontWeight: '800' }}>₹{expensesByCategory[selectedCategory]?.toFixed(2) || 0}</h2>
          </div>
        )}

        <div className="transactions-list" style={{ marginTop: '16px' }}>
          {displayedTransactions.length === 0 ? (
            <p style={{ color: '#888', textAlign: 'center', padding: '20px 0' }}>No transactions found for this category.</p>
          ) : (
            displayedTransactions.map(tx => (
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
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default MoneyDashboard;
