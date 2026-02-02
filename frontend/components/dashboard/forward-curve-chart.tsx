"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from 'react';
import { fetchCurve } from '@/lib/api';

interface CurveData {
    name: string;
    Price: number;
}

export function ForwardCurveChart() {
    const [data, setData] = useState<CurveData[]>([]);

    useEffect(() => {
        async function loadData() {
            try {
                const curvePoints = await fetchCurve();
                // Filter for one commodity if multiple exist, or just show all.
                // The CSV has multiple commodities. Let's filter for "Brent Crude" for now or just take the first one found per month?
                // The CSV structure is: curve_date, commodity, tenor, price
                // Let's filter for "Brent Crude"

                const brentCurve = curvePoints.filter((p: any) => p.commodity === 'Brent Crude');

                const chartData = brentCurve.map((p: any) => ({
                    name: p.tenor, // "Dec 25"
                    Price: p.price
                }));

                setData(chartData);
            } catch (error) {
                console.error("Error loading curve:", error);
            }
        }
        loadData();
    }, []);

    return (
        <Card className="col-span-1 h-full">
            <CardHeader>
                <CardTitle>Forward Curve (Brent Crude)</CardTitle>
            </CardHeader>
            <CardContent className="pl-2">
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
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
                            <YAxis domain={['auto', 'auto']} />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="Price" stroke="#8884d8" activeDot={{ r: 8 }} strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
