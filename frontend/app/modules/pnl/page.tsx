"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PnLWaterfallChart } from "@/components/pnl-waterfall-chart"
import { DollarSign, TrendingUp, AlertTriangle } from "lucide-react"

interface PnLResult {
    delta_pnl: number
    new_deal_pnl: number
    unexplained_pnl: number
    total_calculated_pnl: number
    total_reported_pnl: number
}

export default function PnLPage() {
    const [formData, setFormData] = useState({
        yesterday_price: 75.00,
        today_price: 76.00,
        position_volume: 10000,
        new_deal_volume: 1000,
        new_deal_price: 75.50,
        actual_daily_pnl: 10500
    })

    const [result, setResult] = useState<PnLResult | null>(null)
    const [isLoading, setIsLoading] = useState(false)

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: parseFloat(value) || 0
        }))
    }

    const calculatePnL = async () => {
        setIsLoading(true)
        try {
            const response = await fetch("http://localhost:8000/api/pnl/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })

            if (!response.ok) throw new Error("Calculation failed")

            const data = await response.json()
            setResult(data)
        } catch (error) {
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">P&L Attribution Model</h1>
                <p className="text-muted-foreground">
                    Decompose your daily profit into Market Luck (Delta) and Trader Skill (New Deal).
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                <Card className="lg:col-span-1">
                    <CardHeader>
                        <CardTitle>Daily Inputs</CardTitle>
                        <CardDescription>Enter market data and trade details.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="yesterday_price">Yesterday Price ($)</Label>
                                <Input
                                    id="yesterday_price"
                                    name="yesterday_price"
                                    type="number"
                                    step="0.01"
                                    value={formData.yesterday_price}
                                    onChange={handleInputChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="today_price">Today Price ($)</Label>
                                <Input
                                    id="today_price"
                                    name="today_price"
                                    type="number"
                                    step="0.01"
                                    value={formData.today_price}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="position_volume">Existing Position (bbls)</Label>
                            <Input
                                id="position_volume"
                                name="position_volume"
                                type="number"
                                value={formData.position_volume}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="new_deal_volume">New Deal Vol</Label>
                                <Input
                                    id="new_deal_volume"
                                    name="new_deal_volume"
                                    type="number"
                                    value={formData.new_deal_volume}
                                    onChange={handleInputChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="new_deal_price">Deal Price ($)</Label>
                                <Input
                                    id="new_deal_price"
                                    name="new_deal_price"
                                    type="number"
                                    step="0.01"
                                    value={formData.new_deal_price}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        <div className="space-y-2 pt-4 border-t">
                            <Label htmlFor="actual_daily_pnl">Actual Reported P&L ($)</Label>
                            <Input
                                id="actual_daily_pnl"
                                name="actual_daily_pnl"
                                type="number"
                                value={formData.actual_daily_pnl}
                                onChange={handleInputChange}
                            />
                            <p className="text-xs text-muted-foreground">Used to calculate Unexplained P&L</p>
                        </div>

                        <Button className="w-full" onClick={calculatePnL} disabled={isLoading}>
                            {isLoading ? "Calculating..." : "Run Attribution"}
                        </Button>
                    </CardContent>
                </Card>

                <div className="lg:col-span-2 space-y-6">
                    {result && (
                        <>
                            <div className="grid gap-4 md:grid-cols-3">
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">Delta (Market)</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className={`text-2xl font-bold ${result.delta_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            ${result.delta_pnl.toLocaleString()}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">New Deal (Skill)</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className={`text-2xl font-bold ${result.new_deal_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            ${result.new_deal_pnl.toLocaleString()}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">Unexplained</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className={`text-2xl font-bold flex items-center ${result.unexplained_pnl === 0 ? 'text-gray-600' : 'text-yellow-600'}`}>
                                            ${result.unexplained_pnl.toLocaleString()}
                                            {result.unexplained_pnl !== 0 && <AlertTriangle className="ml-2 h-4 w-4" />}
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            <Card>
                                <CardHeader>
                                    <CardTitle>P&L by Driver</CardTitle>
                                    <CardDescription>Visual breakdown of profit sources.</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <PnLWaterfallChart data={result} />
                                </CardContent>
                            </Card>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
