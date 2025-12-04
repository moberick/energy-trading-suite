"use client"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface Position {
    commodity: string
    delivery_month: string
    net_volume: number
    exposure_status: string
}

interface PositionTableProps {
    positions: Position[]
}

export function PositionTable({ positions }: PositionTableProps) {
    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Commodity</TableHead>
                        <TableHead>Delivery Month</TableHead>
                        <TableHead className="text-right">Net Volume</TableHead>
                        <TableHead className="text-center">Status</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {positions.length === 0 ? (
                        <TableRow>
                            <TableCell colSpan={4} className="h-24 text-center">
                                No data available. Upload a trade file to see positions.
                            </TableCell>
                        </TableRow>
                    ) : (
                        positions.map((pos, index) => (
                            <TableRow key={index}>
                                <TableCell className="font-medium">{pos.commodity}</TableCell>
                                <TableCell>{pos.delivery_month}</TableCell>
                                <TableCell className={`text-right font-mono ${pos.net_volume !== 0 ? 'text-red-600 font-bold' : 'text-green-600'}`}>
                                    {pos.net_volume.toLocaleString()}
                                </TableCell>
                                <TableCell className="text-center">
                                    <Badge
                                        variant={pos.exposure_status === "Flat" ? "outline" : "destructive"}
                                        className={pos.exposure_status === "Flat" ? "bg-green-100 text-green-800 border-green-200" : ""}
                                    >
                                        {pos.exposure_status}
                                    </Badge>
                                </TableCell>
                            </TableRow>
                        ))
                    )}
                </TableBody>
            </Table>
        </div>
    )
}
