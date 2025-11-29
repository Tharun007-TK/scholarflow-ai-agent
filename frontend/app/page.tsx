"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Upload, FileText, CheckCircle, Loader2 } from "lucide-react"

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      })

      if (res.ok) {
        const data = await res.json()
        localStorage.setItem("dashboardData", JSON.stringify(data))
        router.push("/dashboard")
      } else {
        console.error("Upload failed")
        alert("Upload failed. Please check the backend logs.")
      }
    } catch (error) {
      console.error("Error uploading file:", error)
      alert("Error uploading file. Is the backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-4 text-center max-w-3xl mx-auto">
      <div className="space-y-4 mb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight lg:text-6xl">
          Academic Workflow <br className="hidden sm:block" />
          <span className="text-primary">Automation</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-[600px] mx-auto">
          Upload your course material and let our AI agents organize your study life.
          Generate tasks, summaries, and schedules instantly.
        </p>
      </div>

      <div className="w-full max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-150">
        <div className="border-2 border-dashed rounded-xl p-10 hover:bg-muted/50 transition-colors relative group">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />
          <div className="flex flex-col items-center gap-4">
            <div className="p-4 bg-primary/5 rounded-full group-hover:bg-primary/10 transition-colors">
              <Upload className="h-8 w-8 text-primary" />
            </div>
            <div className="space-y-1">
              <p className="font-semibold">
                {file ? file.name : "Upload Syllabus or Notes"}
              </p>
              <p className="text-sm text-muted-foreground">
                Drag and drop or click to select a PDF file
              </p>
            </div>
            {file && (
              <span className="text-xs font-medium px-2 py-1 bg-primary/10 text-primary rounded">
                Selected
              </span>
            )}
          </div>
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-semibold text-lg hover:bg-primary/90 disabled:opacity-50 transition-all shadow-lg hover:shadow-xl disabled:shadow-none flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Processing...
            </>
          ) : (
            "Start TaskFlow Pipeline"
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-16 w-full text-left animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
        <div className="p-4 border rounded-xl bg-card/50 backdrop-blur-sm">
          <CheckCircle className="h-6 w-6 text-primary mb-2" />
          <h3 className="font-semibold">Smart Parsing</h3>
          <p className="text-sm text-muted-foreground">Extracts tasks and deadlines automatically.</p>
        </div>
        <div className="p-4 border rounded-xl bg-card/50 backdrop-blur-sm">
          <CheckCircle className="h-6 w-6 text-primary mb-2" />
          <h3 className="font-semibold">Study Schedule</h3>
          <p className="text-sm text-muted-foreground">Generates a day-wise study plan.</p>
        </div>
        <div className="p-4 border rounded-xl bg-card/50 backdrop-blur-sm">
          <CheckCircle className="h-6 w-6 text-primary mb-2" />
          <h3 className="font-semibold">AI Summaries</h3>
          <p className="text-sm text-muted-foreground">Concise summaries and flashcards.</p>
        </div>
      </div>
    </div>
  )
}
