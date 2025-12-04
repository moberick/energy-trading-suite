import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart3, Activity, ShieldCheck, Ship, FileDown } from "lucide-react"

export default function Home() {
  const modules = [
    {
      title: "Position Engine",
      description: "Daily Position & Exposure Aggregation",
      icon: Activity,
      href: "/modules/position",
      color: "text-blue-600",
    },
    {
      title: "P&L Attribution",
      description: "Delta & New Deal P&L Analysis",
      icon: BarChart3,
      href: "/modules/pnl",
      color: "text-green-600",
    },
    {
      title: "Curve Validation",
      description: "Stale Checks & Fly Spreads",
      icon: ShieldCheck,
      href: "/modules/validation",
      color: "text-purple-600",
    },
    {
      title: "Arb Calculator",
      description: "Physical Arbitrage & Freight Logic",
      icon: Ship,
      href: "/modules/arb",
      color: "text-orange-600",
    },
    {
      title: "Flash Report",
      description: "Daily P&L & Exposure PDF Export",
      icon: FileDown,
      href: "/modules/report",
      color: "text-red-600",
    },
  ]

  return (
    <div className="container mx-auto py-10 space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900">Energy Trading Operations Suite</h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto">
          A comprehensive toolkit for the modern commercial analyst.
          Manage exposure, attribute P&L, validate curves, and calculate arbitrage.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {modules.map((module) => (
          <Card key={module.title} className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href={module.href}>
              <CardHeader>
                <module.icon className={`h-10 w-10 ${module.color} mb-2`} />
                <CardTitle>{module.title}</CardTitle>
                <CardDescription>{module.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full justify-start pl-0 hover:bg-transparent hover:text-primary">
                  Launch Module &rarr;
                </Button>
              </CardContent>
            </Link>
          </Card>
        ))}
      </div>
    </div>
  )
}
