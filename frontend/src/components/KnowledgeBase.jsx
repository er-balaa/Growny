import React from 'react';

const KnowledgeBase = () => {
  return (
    <div className="knowledge-base-dashboard">
      <div className="kb-header">
        <h2>My Knowledge Base</h2>
        <p>Your second brain. Upload documents and ask questions.</p>
      </div>
      
      <div className="kb-content">
        <div className="upload-section">
          <div className="upload-dropzone">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="upload-icon">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p className="upload-title">Drag & drop files here</p>
            <p className="upload-subtitle">or click to browse (Coming Soon)</p>
          </div>
        </div>
        
        <div className="documents-section">
          <h3>Your Documents</h3>
          <div className="empty-state">
            <p>No documents uploaded yet. This feature is under construction.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
