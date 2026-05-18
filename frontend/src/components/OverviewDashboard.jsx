import React, { useState } from 'react';
import TaskList from './TaskList';
import { emailAPI } from '../services/api';
import { auth } from '../firebase';

const OverviewDashboard = ({ tasks = [], transactions = [], onDeleteTask }) => {

  // ── Financial Calculations ──────────────────────────────────────
  const totalIncome = transactions
    .filter(t => t.type === 'INCOME')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);

  const totalExpense = transactions
    .filter(t => t.type === 'EXPENSE')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);

  const netWorth = totalIncome - totalExpense;

  // ── Productivity Calculations ───────────────────────────────────
  const now = new Date();
  const completedTasks = tasks.filter(t => t.completed);
  const pendingTasks = tasks.filter(t => !t.completed && t.category === 'TASK');
  const allNotes = tasks.filter(t => t.category === 'NOTE');

  const overdueItems = tasks.filter(t => {
    if (t.completed) return false;
    if (!t.due_date) return false;
    return new Date(t.due_date) < now;
  }).sort((a, b) => new Date(a.due_date) - new Date(b.due_date));

  const upcomingItems = tasks.filter(t => {
    if (t.completed) return false;
    if (overdueItems.includes(t)) return false;
    return t.category !== 'NOTE';
  }).sort((a, b) => {
    const pA = a.priority === 'HIGH' ? 3 : a.priority === 'MEDIUM' ? 2 : 1;
    const pB = b.priority === 'HIGH' ? 3 : b.priority === 'MEDIUM' ? 2 : 1;
    if (pA !== pB) return pB - pA;
    if (a.due_date && b.due_date) return new Date(a.due_date) - new Date(b.due_date);
    if (a.due_date) return -1;
    if (b.due_date) return 1;
    return 0;
  });

  return (
    <div className="overview-dashboard">
      <div className="overview-grid">

        {/* ── Left Analytics Column ─────────────────────────────── */}
        <div className="analytics-column">
          <div className="overview-section-title">
            <h2>Financial Pulse</h2>
          </div>
          <div className="finance-overview compact-finance">
            <div className="finance-card net-worth">
              <span className="card-label">Net Balance</span>
              <h2 className="card-value" style={{ color: netWorth >= 0 ? '#10b981' : '#ef4444' }}>
                ₹{netWorth.toFixed(2)}
              </h2>
            </div>
            <div className="finance-card-row">
              <div className="finance-card income compact">
                <span className="card-label">Income</span>
                <h3 className="card-value text-success">₹{totalIncome.toFixed(2)}</h3>
              </div>
              <div className="finance-card expense compact">
                <span className="card-label">Expense</span>
                <h3 className="card-value text-danger">₹{totalExpense.toFixed(2)}</h3>
              </div>
            </div>
          </div>

          <div className="overview-section-title mt-24">
            <h2>Productivity Pulse</h2>
          </div>
          <div className="productivity-stats">
            <div className="stat-box">
              <div className="stat-number">{pendingTasks.length}</div>
              <div className="stat-label">Pending Tasks</div>
            </div>
            <div className="stat-box">
              <div className="stat-number text-success">{completedTasks.length}</div>
              <div className="stat-label">Completed</div>
            </div>
            <div className="stat-box">
              <div className="stat-number text-muted">{allNotes.length}</div>
              <div className="stat-label">Total Notes</div>
            </div>
          </div>

        </div>

        {/* ── Right Content Column ──────────────────────────────── */}
        <div className="content-column">

          {/* Overdue Section */}
          {overdueItems.length > 0 && (
            <div className="overdue-container">
              <div className="overdue-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <h3>Overdue &amp; Urgent</h3>
                <span className="overdue-badge">{overdueItems.length}</span>
              </div>
              <div className="overdue-list-wrapper">
                <TaskList tasks={overdueItems} onDeleteTask={onDeleteTask} hideHeader={true} />
              </div>
            </div>
          )}

          <div className="overview-section-title mt-24">
            <h2>Active Agenda</h2>
          </div>
          <div className="agenda-list-wrapper">
            {upcomingItems.length > 0 ? (
              <TaskList tasks={upcomingItems} onDeleteTask={onDeleteTask} hideHeader={true} />
            ) : (
              <div className="empty-state">
                <p>You have no active tasks. Take a break!</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default OverviewDashboard;
