"use client"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useEffect, useState } from 'react';
import { fetchPnLAttribution } from '@/lib/api';

interface AttributionData {
    driver: string;
    value: number;
    percentage: string;
}

export function PnlAttributionTable() {
    const [data, setData] = useState<AttributionData[]>([]);

    useEffect(() => {
        async function loadData() {
            try {
                const pnlData = await fetchPnLAttribution();
                // Aggregate by driver
                const driverData: { [key: string]: number } = {};
                let total = 0;

                pnlData.forEach((item: any) => {
                    if (!driverData[item.driver]) {
                        driverData[item.driver] = 0;
                    }
                    driverData[item.driver] += item.pnl_value;
                    total += item.pnl_value;
                });

                const tableData = Object.keys(driverData).map(driver => ({
                    driver: driver,
                    value: driverData[driver],
                    percentage: total !== 0 ? `${Math.round((driverData[driver] / total) * 100)}%` : "0%"
                }));

                setData(tableData);
            } catch (error) {
                console.error("Error loading PnL attribution:", error);
            }
        }
        loadData();
    }, []);

    return (
        <Card className="col-span-1 h-full">
            <CardHeader>
                <CardTitle>P&L Attribution</CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Driver</TableHead>
                            <TableHead className="text-right">Value ($)</TableHead>
                            <TableHead className="text-right">%</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((item) => (
                            <TableRow key={item.driver}>
                                <TableCell className="font-medium">{item.driver}</TableCell>
                                <TableCell className="text-right">
                                    <span className={item.value >= 0 ? "text-green-600" : "text-red-600"}>
                                        {item.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </span>
                                </TableCell>
                                <TableCell className="text-right">{item.percentage}</TableCell>
                            </TableRow>
                        ))}
                        <TableRow className="font-bold bg-muted/50">
                            <TableCell>Total</TableCell>
                            <TableCell className="text-right text-green-600">
                                {(data.reduce((acc, item) => acc + item.value, 0)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </TableCell>
                            <TableCell className="text-right">100%</TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}
