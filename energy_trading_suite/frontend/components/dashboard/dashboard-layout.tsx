"use client"

import { NetPositionChart } from "./net-position-chart"
import { ForwardCurveChart } from "./forward-curve-chart"
import { PnlAttributionTable } from "./pnl-attribution-table"
import { ArbMatrix } from "./arb-matrix"

export function DashboardLayout() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[calc(100vh-200px)] min-h-[500px]">
            <div className="col-span-1">
                <NetPositionChart />
            </div>
            <div className="col-span-1">
                <ForwardCurveChart />
            </div>
            <div className="col-span-1">
                <PnlAttributionTable />
            </div>
            <div className="col-span-1">
                <ArbMatrix />
            </div>
        </div>
    )
}
