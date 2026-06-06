import { Link } from "react-router-dom";
import { FileSearch, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionLink?: string;
}

export function EmptyState({
  title = "No candidates screened yet",
  description = "Upload resumes to begin AI-powered screening and see rankings, analytics, and skill gap analysis.",
  actionLabel = "Upload resumes to begin screening",
  actionLink = "/upload",
}: EmptyStateProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-full bg-primary/10 p-4 mb-4">
          <FileSearch className="h-8 w-8 text-primary" />
        </div>
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground mt-2 max-w-md">{description}</p>
        <Button asChild className="mt-6">
          <Link to={actionLink}>
            <Upload className="h-4 w-4 mr-2" />
            {actionLabel}
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
