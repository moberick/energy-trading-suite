"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Ship, Anchor, DollarSign, Clock } from "lucide-react"

interface ArbResult {
    freight_cost_per_bbl: number
    total_logistics_cost: number
    margin: number
    is_open: boolean
    voyage_days: number
}

export default function ArbPage() {
    const [formData, setFormData] = useState({
        sales_price: 75.00, // Brent
        purchase_price: 70.00, // WTI
        freight_rate: 40000, // $/day
        distance: 4500, // Trans-Atlantic
        speed: 12.0, // Knots
        fuel_consumption: 60, // Tons/day
        fuel_price: 600, // $/ton
        insurance_cost: 0.50, // $/bbl
        volume: 2000000 // VLCC
    })

    const [result, setResult] = useState<ArbResult | null>(null)
    const [isLoading, setIsLoading] = useState(false)

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: parseFloat(value) || 0
        }))
    }

    const handleSpeedChange = (value: number[]) => {
        setFormData(prev => ({
            ...prev,
            speed: value[0]
        }))
    }

    const calculateArb = async () => {
        setIsLoading(true)
        try {
            const response = await fetch("http://localhost:8000/api/arb/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })

            const data = await response.json()
            setResult(data)
        } catch (error) {
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    // Auto-calculate on load
    useEffect(() => {
        calculateArb()
    }, [])

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">Physical Arbitrage Calculator</h1>
                <p className="text-muted-foreground">
                    Calculate Trans-Atlantic margins with variable freight speeds (Slow Steaming).
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                <Card className="lg:col-span-1">
                    <CardHeader>
                        <CardTitle>Voyage Parameters</CardTitle>
                        <CardDescription>Adjust logistics to optimize margin.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Vessel Speed (Knots): {formData.speed}</Label>
                            <Slider
                                value={[formData.speed]}
                                min={8}
                                max={16}
                                step={0.5}
                                onValueChange={handleSpeedChange}
                            />
                            <p className="text-xs text-muted-foreground">Lower speed = Lower fuel cost, Higher charter time.</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4">
                            <div className="space-y-2">
                                <Label htmlFor="sales_price">Sales Price (DES)</Label>
                                <Input
                                    id="sales_price"
                                    name="sales_price"
                                    type="number"
                                    value={formData.sales_price}
                                    onChange={handleInputChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="purchase_price">Buy Price (FOB)</Label>
                                <Input
                                    id="purchase_price"
                                    name="purchase_price"
                                    type="number"
                                    value={formData.purchase_price}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="freight_rate">Daily Hire Rate ($)</Label>
                            <Input
                                id="freight_rate"
                                name="freight_rate"
                                type="number"
                                value={formData.freight_rate}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="fuel_price">Fuel Price ($/t)</Label>
                                <Input
                                    id="fuel_price"
                                    name="fuel_price"
                                    type="number"
                                    value={formData.fuel_price}
                                    onChange={handleInputChange}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="insurance_cost">Insurance ($/bbl)</Label>
                                <Input
                                    id="insurance_cost"
                                    name="insurance_cost"
                                    type="number"
                                    step="0.01"
                                    value={formData.insurance_cost}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        <Button className="w-full" onClick={calculateArb} disabled={isLoading}>
                            {isLoading ? "Calculating..." : "Recalculate"}
                        </Button>
                    </CardContent>
                </Card>

                <div className="lg:col-span-2 space-y-6">
                    {result && (
                        <>
                            <div className={`p-6 rounded-lg border-2 ${result.is_open ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className={`text-2xl font-bold ${result.is_open ? 'text-green-700' : 'text-red-700'}`}>
                                            Arb Window is {result.is_open ? 'OPEN' : 'CLOSED'}
                                        </h2>
                                        <p className="text-gray-600">
                                            Margin: <span className="font-bold">${result.margin.toFixed(2)}/bbl</span>
                                        </p>
                                    </div>
                                    <Ship className={`h-16 w-16 ${result.is_open ? 'text-green-500' : 'text-red-500'}`} />
                                </div>
                            </div>

                            <div className="grid gap-4 md:grid-cols-3">
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">Freight Cost</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold text-gray-900">
                                            ${result.freight_cost_per_bbl.toFixed(2)}<span className="text-sm font-normal text-gray-500">/bbl</span>
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">Total Logistics</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold text-gray-900">
                                            ${result.total_logistics_cost.toFixed(2)}<span className="text-sm font-normal text-gray-500">/bbl</span>
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">Voyage Time</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold text-gray-900">
                                            {result.voyage_days} <span className="text-sm font-normal text-gray-500">days</span>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
