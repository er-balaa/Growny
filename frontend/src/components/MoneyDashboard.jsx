import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, Sector } from 'recharts';

const renderActiveShape = (props) => {
  const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload } = props;
  return (
    <g style={{ outline: 'none', WebkitTapHighlightColor: 'transparent' }}>
      <text x={cx} y={cy - 10} dy={8} textAnchor="middle" fill="#ffffff" style={{ fontSize: '16px', fontWeight: '700', letterSpacing: '-0.3px' }}>
        {payload.name}
      </text>
      <text x={cx} y={cy + 15} dy={8} textAnchor="middle" fill="#a3a3a3" style={{ fontSize: '14px', fontWeight: '600' }}>
        ₹{payload.value.toFixed(0)}
      </text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 6}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
        stroke="rgba(255,255,255,0.15)"
        strokeWidth={2}
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 10}
        outerRadius={outerRadius + 14}
        fill={fill}
        stroke="none"
        opacity={0.3}
      />
    </g>
  );
};

const MoneyDashboard = ({ transactions = [], onDeleteTransaction }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isMobile, setIsMobile] = useState(false);
  const [expandedTxId, setExpandedTxId] = useState(null);

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

  // Premium Apple-inspired vibrant palette
  const COLORS = [
    '#FF3B30', // Red
    '#FF9500', // Orange
    '#FFCC00', // Yellow
    '#34C759', // Green
    '#5AC8FA', // Light Blue
    '#007AFF', // Blue
    '#5856D6', // Purple
    '#FF2D55'  // Pink
  ];

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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700' }}>Expense Analysis</h3>
            <span style={{ fontSize: '13px', color: '#a3a3a3' }}>Tap a category slice for details</span>
          </div>
          
          <div style={{ 
            width: '100%', 
            height: isMobile ? 360 : 380, 
            background: 'rgba(30, 30, 30, 0.65)', 
            backdropFilter: 'blur(24px)', 
            WebkitBackdropFilter: 'blur(24px)', 
            borderRadius: '24px', 
            padding: isMobile ? '20px 10px' : '24px', 
            border: '1px solid rgba(255, 255, 255, 0.08)',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.06)' 
          }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  activeIndex={activeIndex}
                  activeShape={renderActiveShape}
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="45%"
                  outerRadius={isMobile ? 95 : 120}
                  innerRadius={isMobile ? 70 : 85}
                  paddingAngle={3}
                  stroke="none"
                  labelLine={false}
                  label={false}
                  onClick={handlePieClick}
                >
                  {pieData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[index % COLORS.length]} 
                      stroke="none"
                      style={{ outline: 'none', cursor: 'pointer', transition: 'all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)', WebkitTapHighlightColor: 'transparent' }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => `₹${value.toFixed(2)}`}
                  contentStyle={{ backgroundColor: 'rgba(40,40,40,0.85)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.4)' }}
                  itemStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={isMobile ? 80 : 50} 
                  iconType="circle" 
                  wrapperStyle={{ 
                    fontSize: isMobile ? '12px' : '13px', 
                    color: '#e5e5e5', 
                    paddingTop: '20px',
                    lineHeight: '24px'
                  }} 
                />
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
                  {tx.type === 'INCOME' ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <polyline points="19 12 12 19 5 12"></polyline>
                    </svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect>
                      <line x1="2" y1="10" x2="22" y2="10"></line>
                    </svg>
                  )}
                </div>
                <div 
                  className="tx-details" 
                  onClick={() => setExpandedTxId(expandedTxId === tx.id ? null : tx.id)}
                  style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '6px' }}
                  title="Tap to expand details"
                >
                  <div className="tx-header" style={{ marginBottom: 0 }}>
                    <span className="tx-category-title" style={{ fontSize: '16px', fontWeight: '800', color: '#fff', letterSpacing: '0.5px' }}>
                      {tx.category || 'General'}
                    </span>
                    <span className={`tx-amount ${tx.type.toLowerCase()}`}>
                      {tx.type === 'INCOME' ? '+' : '-'}₹{tx.amount.toFixed(2)}
                    </span>
                  </div>
                  
                  <div className="tx-description-row" style={{ display: 'flex', flexDirection: 'column', gap: '4px', width: '100%' }}>
                    <span className={`tx-desc ${expandedTxId === tx.id ? 'expanded' : ''}`} style={{ fontSize: '14px', color: '#a3a3a3', fontWeight: '500' }}>
                      {tx.description}
                    </span>
                    <span className="tx-date" style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                      {formatDate(tx.date)}
                    </span>
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
