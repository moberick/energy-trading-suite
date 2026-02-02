"use client"

import { useState } from "react"
import { FileUploader } from "@/components/file-uploader"
import { PositionTable } from "@/components/position-table"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, CheckCircle2 } from "lucide-react"

interface Position {
    commodity: string
    delivery_month: string
    net_volume: number
    exposure_status: string
}

export default function PositionPage() {
    const [positions, setPositions] = useState<Position[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleUpload = async (file: File) => {
        setIsLoading(true)
        setError(null)

        const formData = new FormData()
        formData.append("file", file)

        try {
            const response = await fetch("http://localhost:8000/api/trades/upload", {
                method: "POST",
                body: formData,
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Failed to upload file")
            }

            const data = await response.json()
            setPositions(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : "An unknown error occurred")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">Daily Position & Exposure Engine</h1>
                <p className="text-muted-foreground">
                    Aggregate physical and paper deals to visualize your Net Position.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Upload Trades</CardTitle>
                        <CardDescription>
                            Upload your daily trade dump (CSV) to calculate exposure.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <FileUploader onUpload={handleUpload} isLoading={isLoading} />
                        {error && (
                            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md flex items-center text-sm">
                                <AlertCircle className="h-4 w-4 mr-2" />
                                {error}
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Exposure Summary</CardTitle>
                        <CardDescription>
                            Real-time view of your net position by commodity and month.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex items-center justify-center h-[200px]">
                        {positions.length > 0 ? (
                            <div className="text-center">
                                <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-2" />
                                <p className="text-lg font-medium">Analysis Complete</p>
                                <p className="text-sm text-gray-500">{positions.length} positions calculated</p>
                            </div>
                        ) : (
                            <p className="text-gray-400">Waiting for data...</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Detailed Position Report</CardTitle>
                </CardHeader>
                <CardContent>
                    <PositionTable positions={positions} />
                </CardContent>
            </Card>
        </div>
    )
}
