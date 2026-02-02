"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from 'react';
import { fetchPositions } from '@/lib/api';

interface ChartData {
    name: string;
    Long: number;
    Short: number;
}

export function NetPositionChart() {
    const [data, setData] = useState<ChartData[]>([]);

    useEffect(() => {
        async function loadData() {
            try {
                const positions = await fetchPositions();
                // Aggregate by month
                const monthlyData: { [key: string]: { Long: number, Short: number } } = {};

                positions.forEach((pos: any) => {
                    const month = pos.delivery_month;
                    if (!monthlyData[month]) {
                        monthlyData[month] = { Long: 0, Short: 0 };
                    }
                    if (pos.exposure_status === 'Long') {
                        monthlyData[month].Long += pos.net_volume;
                    } else if (pos.exposure_status === 'Short') {
                        monthlyData[month].Short += Math.abs(pos.net_volume);
                    }
                });

                const chartData = Object.keys(monthlyData).map(month => ({
                    name: month,
                    Long: monthlyData[month].Long,
                    Short: monthlyData[month].Short
                }));

                // Sort by month (simple sort for now, assuming format "Mon YY")
                // A better sort would parse the date.
                // For now let's just trust the order or basic string sort? 
                // The CSV has "Dec 25", "Jan 26". String sort won't work well.
                // Let's leave it unsorted or sort by appearance in CSV if possible.
                // Or just simple sort.

                setData(chartData);
            } catch (error) {
                console.error("Error loading positions:", error);
            }
        }
        loadData();
    }, []);

    return (
        <Card className="col-span-1 h-full">
            <CardHeader>
                <CardTitle>Net Position</CardTitle>
            </CardHeader>
            <CardContent className="pl-2">
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={data}
                            margin={{
                                top: 5,
                                right: 30,
                                left: 20,
                                bottom: 5,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="Long" fill="#22c55e" />
                            <Bar dataKey="Short" fill="#ef4444" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
