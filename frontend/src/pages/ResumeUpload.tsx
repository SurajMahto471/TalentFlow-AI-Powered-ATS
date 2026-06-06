import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertCircle, CheckCircle, FileText, Loader2, Play, Sparkles, Upload, X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useScreening } from "@/contexts/ScreeningContext";
import { SAMPLE_JOB_DESCRIPTION, createSampleCsvFile } from "@/data/sampleData";

export function ResumeUpload() {
  const navigate = useNavigate();
  const { runAIScreening, isScreening, error, clearResults, hasResults } = useScreening();
  const [jobDescription, setJobDescription] = useState("");
  const [rawFiles, setRawFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [success, setSuccess] = useState(false);

  const addFiles = (fileList: File[]) => {
    const valid = fileList.filter((f) => /\.(pdf|docx|csv)$/i.test(f.name));
    setRawFiles((prev) => {
      const names = new Set(prev.map((f) => f.name));
      return [...prev, ...valid.filter((f) => !names.has(f.name))];
    });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    addFiles(Array.from(e.dataTransfer.files));
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) addFiles(Array.from(e.target.files));
    e.target.value = "";
  };

  const runScreeningAndRedirect = async (jd: string, files: File[]) => {
    setSuccess(false);
    await runAIScreening(jd, files);
    setSuccess(true);
    setTimeout(() => navigate("/"), 1500);
  };

  const handleScreening = async () => {
    if (!jobDescription.trim() || rawFiles.length === 0) return;
    try {
      await runScreeningAndRedirect(jobDescription, rawFiles);
    } catch {
      /* error shown via context */
    }
  };

  const handleLoadSampleJD = () => {
    setJobDescription(SAMPLE_JOB_DESCRIPTION);
  };

  const handleDemoScreening = async () => {
    const sampleFile = createSampleCsvFile();
    setJobDescription(SAMPLE_JOB_DESCRIPTION);
    setRawFiles([sampleFile]);
    try {
      await runScreeningAndRedirect(SAMPLE_JOB_DESCRIPTION, [sampleFile]);
    } catch {
      /* error shown via context */
    }
  };

  const formatSize = (bytes: number) =>
    bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI Screening</h1>
          <p className="text-muted-foreground">
            Paste a job description, upload resumes, and run NLP-powered ATS scoring
          </p>
        </div>
        {hasResults && (
          <Button variant="outline" onClick={clearResults}>
            Clear Previous Results
          </Button>
        )}
      </div>

      <div className="flex flex-wrap gap-3">
        <Button type="button" variant="outline" onClick={handleLoadSampleJD}>
          Load Sample Job Description
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={handleDemoScreening}
          disabled={isScreening}
        >
          {isScreening ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Play className="h-4 w-4 mr-2" />
          )}
          Run Demo Screening (5 candidates)
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Job Description</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder={`Python Developer\n\nRequired Skills:\nPython, SQL, Django, Docker\n\nExperience: 3+ Years`}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            className="min-h-[180px]"
          />
        </CardContent>
      </Card>

      <Card
        className={`border-2 border-dashed transition-all duration-300 ${
          dragging ? "border-primary bg-primary/5" : "border-border"
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <CardContent className="flex flex-col items-center justify-center py-12">
          <div className="rounded-full bg-primary/10 p-4 mb-4">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-lg font-semibold">Upload Resumes</h3>
          <p className="text-sm text-muted-foreground mt-1">PDF, DOCX, or CSV — multiple files supported</p>
          <div className="mt-4">
            <input
              id="resume-file-input"
              type="file"
              multiple
              accept=".pdf,.docx,.csv"
              className="hidden"
              onChange={handleFileInput}
            />
            <Button type="button" variant="outline" onClick={() => document.getElementById("resume-file-input")?.click()}>
              Browse Files
            </Button>
          </div>
        </CardContent>
      </Card>

      <AnimatePresence>
        {rawFiles.length > 0 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
            {rawFiles.map((f, i) => (
              <Card key={`${f.name}-${i}`}>
                <CardContent className="flex items-center gap-4 p-4">
                  <FileText className="h-6 w-6 text-primary shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{f.name}</p>
                    <p className="text-xs text-muted-foreground">{formatSize(f.size)}</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setRawFiles((prev) => prev.filter((_, idx) => idx !== i))}>
                    <X className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Screening failed</p>
            <p className="mt-1">{error}</p>
            <p className="mt-2 text-xs">Make sure the API is running: <code>python -m uvicorn api:app --reload --port 8000</code></p>
          </div>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-900/20 dark:text-emerald-400">
          <CheckCircle className="h-5 w-5" />
          Screening complete! Redirecting to dashboard...
        </div>
      )}

      <Button
        className="w-full h-12 text-base"
        onClick={handleScreening}
        disabled={isScreening || !jobDescription.trim() || rawFiles.length === 0}
      >
        {isScreening ? (
          <><Loader2 className="h-5 w-5 mr-2 animate-spin" /> Running AI Screening...</>
        ) : (
          <><Sparkles className="h-5 w-5 mr-2" /> Run AI Screening</>
        )}
      </Button>
    </div>
  );
}
