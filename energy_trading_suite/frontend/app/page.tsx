import { DashboardLayout } from "@/components/dashboard/dashboard-layout"

export default function Home() {
  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Energy Trading Operations Suite</h1>
          <p className="text-muted-foreground">
            Daily Position, Forward Curve, and P&L Attribution
          </p>
        </div>
        <div className="flex gap-2">
          {/* Placeholder for future nav or actions */}
        </div>
      </div>

      <DashboardLayout />

      {/* 
        We can add the module links back here or in a sidebar later if needed. 
        For now, the dashboard is the priority.
      */}
    </div>
  )
}
