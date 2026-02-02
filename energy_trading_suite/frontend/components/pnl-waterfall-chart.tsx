"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

interface PnLResult {
    delta_pnl: number
    new_deal_pnl: number
    unexplained_pnl: number
    total_reported_pnl: number
}

interface PnLWaterfallChartProps {
    data: PnLResult
}

export function PnLWaterfallChart({ data }: PnLWaterfallChartProps) {
    // Prepare data for waterfall chart
    // We need to construct the bars so they stack correctly or appear as floating bars
    // For simplicity in Recharts, we can use a custom shape or just separate bars if we want a true waterfall,
    // but a simple bar chart comparing the buckets is often clearer for this use case.
    // However, the user asked for "P&L by Driver", which usually implies a breakdown.

    const chartData = [
        {
            name: 'Delta (Market)',
            value: data.delta_pnl,
            fill: data.delta_pnl >= 0 ? '#22c55e' : '#ef4444',
        },
        {
            name: 'New Deal (Skill)',
            value: data.new_deal_pnl,
            fill: data.new_deal_pnl >= 0 ? '#22c55e' : '#ef4444',
        },
        {
            name: 'Unexplained',
            value: data.unexplained_pnl,
            fill: '#eab308', // Yellow for warning/unexplained
        },
        {
            name: 'Total P&L',
            value: data.total_reported_pnl,
            fill: '#3b82f6', // Blue for total
        },
    ]

    return (
        <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip
                        formatter={(value: number) => [`$${value.toLocaleString()}`, 'P&L']}
                        cursor={{ fill: 'transparent' }}
                    />
                    <ReferenceLine y={0} stroke="#000" />
                    <Bar dataKey="value">
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
