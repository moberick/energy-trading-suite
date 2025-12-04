"use client"

import { useState, useEffect } from "react"
import { PDFDownloadLink } from "@react-pdf/renderer"
import { FlashReportPDF } from "@/components/flash-report-pdf"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileDown, Loader2 } from "lucide-react"

export default function ReportPage() {
    const [isClient, setIsClient] = useState(false)

    // Mock data for the report - in a real app, this would be fetched from context or APIs
    const reportData = {
        date: new Date().toLocaleDateString(),
        pnlData: {
            delta: 10000,
            newDeal: 500,
            unexplained: 0,
            total: 10500
        },
        positionData: [
            { commodity: "Brent", netVolume: 0, status: "Flat" },
            { commodity: "WTI", netVolume: 10000, status: "Long" }
        ],
        arbData: {
            isOpen: true,
            margin: 3.81
        }
    }

    useEffect(() => {
        setIsClient(true)
    }, [])

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">Daily Flash Report</h1>
                <p className="text-muted-foreground">
                    Generate and export the daily commercial summary.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Export Report</CardTitle>
                    <CardDescription>
                        Download the daily summary as a PDF file for distribution.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {isClient ? (
                        <PDFDownloadLink
                            document={<FlashReportPDF {...reportData} />}
                            fileName={`flash_report_${new Date().toISOString().split('T')[0]}.pdf`}
                        >
                            {({ blob, url, loading, error }) => (
                                <Button disabled={loading} className="w-full sm:w-auto">
                                    {loading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Generating PDF...
                                        </>
                                    ) : (
                                        <>
                                            <FileDown className="mr-2 h-4 w-4" />
                                            Download Flash Report
                                        </>
                                    )}
                                </Button>
                            )}
                        </PDFDownloadLink>
                    ) : (
                        <Button disabled>Loading...</Button>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
