"use client";

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface VisualizerProps {
  datasetProfile: {
    profiling_summary: {
      descriptive_stats: Record<string, { mean: number; max: number; min: number }>;
    };
  };
}

export function DataVisualizer({ datasetProfile }: VisualizerProps) {
  const stats = datasetProfile.profiling_summary?.descriptive_stats || {};
  
  const chartData = Object.keys(stats).map(key => ({
    name: key,
    MeanValue: stats[key].mean,
    MaxValue: stats[key].max
  }));

  if (chartData.length === 0) {
    return <p className="text-slate-400 text-sm">No structured numerical vectors found to display visualization summaries.</p>;
  }

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
          <Bar dataKey="MeanValue" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
