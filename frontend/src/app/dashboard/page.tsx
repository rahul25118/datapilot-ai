"use client";

import React, { useState, useEffect } from 'react';
import { DataVisualizer } from '@/components/data-visualizer';
import { ChatInterface } from '@/components/chat-interface';

export default function EnterpriseDashboard() {
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [profileData, setProfileData] = useState<any>(null);
  const [uploading, setUploading] = useState(false);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("datapilot_token");
      const res = await fetch("http://localhost:8000/api/datasets/upload", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      setSelectedDatasetId(data.dataset_id);
    } catch (err) {
      console.error("Infrastructure data flow execution failure:", err);
    } finally {
      setUploading(false);
    }
  }

  useEffect(() => {
    if (!selectedDatasetId) return;
    const token = localStorage.getItem("datapilot_token");
    
    const interval = setInterval(async () => {
      const res = await fetch(`http://localhost:8000/api/datasets/${selectedDatasetId}/profile`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.profiling_summary) {
          setProfileData(data);
          clearInterval(interval);
        }
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedDatasetId]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-8 font-sans">
      <header className="flex justify-between items-center border-b border-slate-800 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">DataPilot AI</h1>
          <p className="text-slate-400 text-sm">Enterprise Executive Semantic Processing Hub</p>
        </div>
        <div className="flex items-center gap-4">
          <input 
            type="file" 
            id="file-upload" 
            className="hidden" 
            accept=".csv,.xlsx,.xls" 
            onChange={handleFileUpload}
          />
          <label 
            htmlFor="file-upload" 
            className={`px-4 py-2 bg-indigo-600 text-sm font-semibold rounded-md cursor-pointer hover:bg-indigo-500 transition-colors ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
          >
            {uploading ? "Processing Framework..." : "Ingest Business Data"}
          </label>
        </div>
      </header>

      {profileData ? (
        <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Data Matrix Scale</p>
                <p className="text-2xl font-bold text-white">{profileData.row_count?.toLocaleString()} Rows</p>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Structural Parameters</p>
                <p className="text-2xl font-bold text-white">{profileData.column_count} Dimensions</p>
              </div>
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Data Integrity Index</p>
                <p className="text-2xl font-bold text-emerald-400">{profileData.profiling_summary?.data_quality_score}%</p>
              </div>
            </div>
            
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Structural Data Vector Analysis Visualization</h3>
              <DataVisualizer datasetProfile={profileData} />
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
              <ChatInterface datasetId={selectedDatasetId!} />
            </div>
          </div>
        </main>
      ) : (
        <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-2xl p-20 text-center max-w-2xl mx-auto mt-12">
          <p className="text-slate-300 font-medium mb-1">No execution context active</p>
          <p className="text-slate-500 text-sm mb-6">Upload a business CSV or Excel file above to spin up the automated real-time statistical profile engine matrices.</p>
        </div>
      )}
    </div>
  );
}
