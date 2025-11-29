"use client"

import { useEffect, useState } from "react"
import { History as HistoryIcon, FileText, Calendar, Layers, CheckSquare } from "lucide-react"

interface HistoryItem {
    timestamp: string
    filename: string
    summary: string
    tasks_count: number
    flashcards_count: number
    schedule_count: number
}

export default function HistoryPage() {
    const [history, setHistory] = useState<HistoryItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/history')
                if (res.ok) {
                    const data = await res.json()
                    setHistory(data)
                }
            } catch (error) {
                console.error("Failed to fetch history:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchHistory()
    }, [])

    return (
        <div className="space-y-8 max-w-5xl mx-auto">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">History</h2>
                <p className="text-muted-foreground">View your past study sessions.</p>
            </div>

            {loading ? (
                <div className="flex justify-center py-10">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            ) : history.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 border rounded-lg bg-muted/10 border-dashed">
                    <HistoryIcon className="h-10 w-10 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No history available yet.</p>
                    <p className="text-xs text-muted-foreground mt-2">
                        Upload a file in Home to start tracking.
                    </p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {history.slice().reverse().map((item, i) => (
                        <div key={i} className="p-6 border rounded-xl bg-card hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-primary/10 rounded-lg">
                                        <FileText className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-lg">{item.filename}</h3>
                                        <p className="text-xs text-muted-foreground">{item.timestamp}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-4 mb-4">
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <CheckSquare className="h-4 w-4" />
                                    <span>{item.tasks_count} Tasks</span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Layers className="h-4 w-4" />
                                    <span>{item.flashcards_count} Flashcards</span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Calendar className="h-4 w-4" />
                                    <span>{item.schedule_count} Sessions</span>
                                </div>
                            </div>

                            <div className="p-4 bg-muted/50 rounded-lg text-sm text-muted-foreground line-clamp-2">
                                {item.summary}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
