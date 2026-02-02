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
import { fetchArbOptimize } from '@/lib/api';

interface RouteData {
    destination: string;
    netback: number;
    voyage_days: number;
}

export function ArbMatrix() {
    const [data, setData] = useState<RouteData[]>([]);
    const [bestDest, setBestDest] = useState<string | null>(null);

    useEffect(() => {
        async function loadData() {
            try {
                const result = await fetchArbOptimize("USGC");
                setData(result.all_routes);
                setBestDest(result.best_destination);
            } catch (error) {
                console.error("Error loading Arb data:", error);
            }
        }
        loadData();
    }, []);

    return (
        <Card className="col-span-1 h-full">
            <CardHeader>
                <CardTitle>LNG Arbitrage (USGC FOB)</CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Destination</TableHead>
                            <TableHead className="text-right">Netback ($)</TableHead>
                            <TableHead className="text-right">Days</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((item) => (
                            <TableRow key={item.destination} className={item.destination === bestDest ? "bg-green-100 dark:bg-green-900" : ""}>
                                <TableCell className="font-medium">{item.destination}</TableCell>
                                <TableCell className="text-right">
                                    {item.netback.toFixed(3)}
                                </TableCell>
                                <TableCell className="text-right">{item.voyage_days}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}
