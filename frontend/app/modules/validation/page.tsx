"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle, History } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface CurvePoint {
    month: string
    price: number
    yesterday_price: number
}

interface ValidationAlert {
    month: string
    check_type: string
    message: string
    severity: string
}

interface AuditLog {
    timestamp: string
    user: string
    action: string
    details: string
}

export default function ValidationPage() {
    const [curve, setCurve] = useState<CurvePoint[]>([
        { month: "Jan 26", price: 70.00, yesterday_price: 70.00 }, // Stale
        { month: "Feb 26", price: 72.00, yesterday_price: 70.50 }, // Fly Check (70+70)/2 = 70. Diff 2.0 > 1.0 (Winter)
        { month: "Mar 26", price: 70.00, yesterday_price: 70.00 },
        { month: "Apr 26", price: 69.50, yesterday_price: 69.80 },
        { month: "May 26", price: 69.00, yesterday_price: 69.20 },
    ])

    const [alerts, setAlerts] = useState<ValidationAlert[]>([])
    const [logs, setLogs] = useState<AuditLog[]>([])
    const [isValid, setIsValid] = useState<boolean | null>(null)
    const [isLoading, setIsLoading] = useState(false)

    const handlePriceChange = (index: number, field: 'price' | 'yesterday_price', value: string) => {
        const newCurve = [...curve]
        newCurve[index] = { ...newCurve[index], [field]: parseFloat(value) || 0 }
        setCurve(newCurve)
    }

    const validateCurve = async () => {
        setIsLoading(true)
        try {
            const response = await fetch("http://localhost:8000/api/curve/validate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(curve)
            })

            const data = await response.json()
            setAlerts(data.alerts)
            setIsValid(data.is_valid)
            fetchLogs()
        } catch (error) {
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    const fetchLogs = async () => {
        try {
            const response = await fetch("http://localhost:8000/api/curve/audit-logs")
            const data = await response.json()
            setLogs(data)
        } catch (error) {
            console.error(error)
        }
    }

    useEffect(() => {
        fetchLogs()
    }, [])

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">Curve Integrity & Validation</h1>
                <p className="text-muted-foreground">
                    Automated "Policeman" for Forward Curves. Detects stale prices and unrealistic spreads.
                </p>
            </div>

            <Tabs defaultValue="validation" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="validation">Validation</TabsTrigger>
                    <TabsTrigger value="audit">Audit Logs</TabsTrigger>
                </TabsList>

                <TabsContent value="validation" className="space-y-4">
                    <div className="grid gap-6 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Forward Curve Input</CardTitle>
                                <CardDescription>Edit prices to test validation rules.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Month</TableHead>
                                            <TableHead>Today ($)</TableHead>
                                            <TableHead>Yesterday ($)</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {curve.map((point, index) => (
                                            <TableRow key={index}>
                                                <TableCell className="font-medium">{point.month}</TableCell>
                                                <TableCell>
                                                    <Input
                                                        type="number"
                                                        step="0.01"
                                                        value={point.price}
                                                        onChange={(e) => handlePriceChange(index, 'price', e.target.value)}
                                                        className="w-24"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Input
                                                        type="number"
                                                        step="0.01"
                                                        value={point.yesterday_price}
                                                        onChange={(e) => handlePriceChange(index, 'yesterday_price', e.target.value)}
                                                        className="w-24"
                                                    />
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                                <div className="mt-4">
                                    <Button className="w-full" onClick={validateCurve} disabled={isLoading}>
                                        {isLoading ? "Validating..." : "Run Validation Checks"}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Validation Results</CardTitle>
                                <CardDescription>Alerts and warnings.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {isValid === true && (
                                    <div className="flex flex-col items-center justify-center py-8 text-green-600">
                                        <CheckCircle className="h-16 w-16 mb-4" />
                                        <p className="text-lg font-medium">Curve is Valid</p>
                                        <p className="text-sm text-gray-500">No issues detected.</p>
                                    </div>
                                )}

                                {alerts.length > 0 && (
                                    <div className="space-y-4">
                                        {alerts.map((alert, index) => (
                                            <div key={index} className={`p-4 rounded-lg border ${alert.severity === 'High' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'}`}>
                                                <div className="flex items-start">
                                                    <AlertCircle className={`h-5 w-5 mr-2 ${alert.severity === 'High' ? 'text-red-600' : 'text-yellow-600'}`} />
                                                    <div>
                                                        <h4 className={`font-medium ${alert.severity === 'High' ? 'text-red-900' : 'text-yellow-900'}`}>
                                                            {alert.check_type} Alert ({alert.month})
                                                        </h4>
                                                        <p className={`text-sm ${alert.severity === 'High' ? 'text-red-700' : 'text-yellow-700'}`}>
                                                            {alert.message}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {isValid === null && !isLoading && (
                                    <div className="text-center py-8 text-gray-400">
                                        Run validation to see results.
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="audit">
                    <Card>
                        <CardHeader>
                            <CardTitle>Audit Logs</CardTitle>
                            <CardDescription>Track who changed what and when.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Timestamp</TableHead>
                                        <TableHead>User</TableHead>
                                        <TableHead>Action</TableHead>
                                        <TableHead>Details</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {logs.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={4} className="text-center py-8 text-gray-500">
                                                No logs available.
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        logs.map((log, index) => (
                                            <TableRow key={index}>
                                                <TableCell className="font-mono text-xs text-gray-500">
                                                    {new Date(log.timestamp).toLocaleString()}
                                                </TableCell>
                                                <TableCell>{log.user}</TableCell>
                                                <TableCell><Badge variant="outline">{log.action}</Badge></TableCell>
                                                <TableCell className="text-sm text-gray-600">{log.details}</TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
