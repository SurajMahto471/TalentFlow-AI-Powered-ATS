import { motion } from "framer-motion";
import { TrendingDown, TrendingUp, type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  growth: number;
  icon: LucideIcon;
  iconColor?: string;
  delay?: number;
}

export function StatCard({ title, value, growth, icon: Icon, iconColor = "text-primary", delay = 0 }: StatCardProps) {
  const isPositive = growth >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className="group overflow-hidden transition-all duration-300 hover:shadow-elevated hover:-translate-y-0.5">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <motion.p
                className="text-3xl font-bold tracking-tight"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: delay + 0.2 }}
              >
                {value}
              </motion.p>
              <div className={cn("flex items-center gap-1 text-xs font-medium", isPositive ? "text-emerald-600" : "text-red-500")}>
                {isPositive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                <span>{isPositive ? "+" : ""}{growth}% vs last month</span>
              </div>
            </div>
            <div className={cn("rounded-xl bg-primary/10 p-3 transition-transform group-hover:scale-110", iconColor)}>
              <Icon className="h-6 w-6" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
