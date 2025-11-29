"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar, CheckSquare, Layers, BookOpen, ExternalLink, Link as LinkIcon, Loader2 } from "lucide-react"

// Simple Card Component since we don't have shadcn/ui installed fully yet
function MetricCard({ title, value, icon: Icon }: { title: string, value: string | number, icon: any }) {
    return (
        <div className="p-6 bg-card rounded-xl border shadow-sm flex items-center justify-between hover:shadow-md transition-shadow">
            <div>
                <p className="text-sm font-medium text-muted-foreground">{title}</p>
                <h3 className="text-2xl font-bold mt-1">{value}</h3>
            </div>
            <div className="p-3 bg-primary/10 rounded-full">
                <Icon className="h-6 w-6 text-primary" />
            </div>
        </div>
    )
}

export default function Dashboard() {
    const [data, setData] = useState<any>(null)
    const [isCalendarConnected, setIsCalendarConnected] = useState(false)
    const [addingToCalendar, setAddingToCalendar] = useState<string | null>(null)

    useEffect(() => {
        const storedData = localStorage.getItem("dashboardData")
        if (storedData) {
            setData(JSON.parse(storedData))
        }
        // Check if we have a token (simplified check)
        // In a real app, we'd check with the backend
    }, [])

    const handleConnectCalendar = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/auth/login')
            if (res.ok) {
                const { url } = await res.json()
                // Open in new window
                window.open(url, 'Google Login', 'width=500,height=600')
                // Assume success for UI state after a delay (simplified)
                setTimeout(() => setIsCalendarConnected(true), 5000)
            } else {
                alert("Failed to initiate login. Is client_secret.json present?")
            }
        } catch (error) {
            console.error(error)
            alert("Error connecting to calendar")
        }
    }

    const addToCalendar = async (item: any) => {
        setAddingToCalendar(item.date + item.task)
        try {
            const res = await fetch('http://localhost:8000/api/calendar/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item)
            })

            if (res.ok) {
                alert("Event added to Google Calendar!")
            } else {
                const err = await res.json()
                if (res.status === 401) {
                    alert("Please connect Google Calendar first.")
                    setIsCalendarConnected(false)
                } else {
                    alert(`Failed to add event: ${err.detail}`)
                }
            }
        } catch (error) {
            console.error(error)
            alert("Error adding event")
        } finally {
            setAddingToCalendar(null)
        }
    }

    if (!data) {
        return (
            <div className="flex items-center justify-center h-full">
                <p className="text-muted-foreground">No data available. Please upload a file in Home.</p>
            </div>
        )
    }

    const { tasks, summary, schedule, flashcards } = data

    return (
        <div className="space-y-8 max-w-5xl mx-auto">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                    <p className="text-muted-foreground">Overview of your study plan and tasks.</p>
                </div>
                {!isCalendarConnected ? (
                    <button
                        onClick={handleConnectCalendar}
                        className="flex items-center gap-2 px-4 py-2 bg-white text-black border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium shadow-sm"
                    >
                        <img src="https://www.google.com/favicon.ico" alt="Google" className="w-4 h-4" />
                        Connect Calendar
                    </button>
                ) : (
                    <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 border border-green-200 rounded-lg text-sm font-medium">
                        <CheckSquare className="w-4 h-4" />
                        Calendar Connected
                    </div>
                )}
            </div>

            <div className="grid gap-4 md:grid-cols-3">
                <MetricCard title="Tasks Found" value={tasks?.length || 0} icon={CheckSquare} />
                <MetricCard title="Flashcards" value={flashcards?.length || 0} icon={Layers} />
                <MetricCard title="Study Sessions" value={schedule?.length || 0} icon={Calendar} />
            </div>

            <div className="w-full">
                {/* Custom Tabs Implementation */}
                <div className="flex border-b mb-6 overflow-x-auto">
                    {['Schedule', 'Summary', 'Flashcards', 'Tasks'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => {
                                const el = document.getElementById(tab.toLowerCase());
                                el?.scrollIntoView({ behavior: 'smooth' });
                            }}
                            className="px-4 py-2 font-medium text-sm text-muted-foreground hover:text-primary transition-colors whitespace-nowrap"
                        >
                            {tab}
                        </button>
                    ))}
                </div>

                <div className="space-y-12">

                    <section id="schedule" className="space-y-4">
                        <h3 className="text-xl font-semibold flex items-center gap-2">
                            <Calendar className="h-5 w-5" /> Study Schedule
                        </h3>
                        <div className="grid gap-4">
                            {schedule?.length > 0 ? schedule.map((item: any, i: number) => (
                                <div key={i} className="p-4 border rounded-lg bg-card flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                                    <div>
                                        <p className="font-semibold">{item.date}</p>
                                        <p className="text-muted-foreground">{item.task}</p>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-sm font-medium px-2 py-1 bg-secondary rounded whitespace-nowrap">
                                            {item.duration_minutes} mins
                                        </span>
                                        <button
                                            onClick={() => addToCalendar(item)}
                                            disabled={addingToCalendar === item.date + item.task}
                                            className="flex items-center gap-1 text-xs font-medium text-primary hover:underline disabled:opacity-50"
                                            title="Add to Google Calendar"
                                        >
                                            {addingToCalendar === item.date + item.task ? (
                                                <Loader2 className="h-3 w-3 animate-spin" />
                                            ) : (
                                                <ExternalLink className="h-3 w-3" />
                                            )}
                                            Add to Calendar
                                        </button>
                                    </div>
                                </div>
                            )) : <p className="text-muted-foreground">No schedule generated.</p>}
                        </div>
                    </section>

                    <section id="summary" className="space-y-4">
                        <h3 className="text-xl font-semibold flex items-center gap-2">
                            <BookOpen className="h-5 w-5" /> Summary
                        </h3>
                        <div className="p-6 border rounded-lg bg-card prose dark:prose-invert max-w-none">
                            <p className="whitespace-pre-wrap leading-relaxed">
                                {typeof summary === 'string' ? summary : summary?.summary || "No summary available."}
                            </p>
                        </div>
                    </section>

                    <section id="flashcards" className="space-y-4">
                        <h3 className="text-xl font-semibold flex items-center gap-2">
                            <Layers className="h-5 w-5" /> Flashcards
                        </h3>
                        <div className="grid gap-4 sm:grid-cols-2">
                            {flashcards?.length > 0 ? flashcards.map((card: any, i: number) => (
                                <div key={i} className="p-6 border rounded-lg bg-card hover:border-primary transition-colors cursor-pointer group">
                                    <p className="font-semibold mb-2 text-primary">Q: {card.front || "Question"}</p>
                                    <p className="text-muted-foreground group-hover:text-foreground transition-colors">A: {card.back || "Answer"}</p>
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        {card.tags?.map((tag: string, j: number) => (
                                            <span key={j} className="text-xs px-2 py-1 bg-secondary rounded-full text-secondary-foreground">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )) : <p className="text-muted-foreground">No flashcards generated.</p>}
                        </div>
                    </section>

                    <section id="tasks" className="space-y-4">
                        <h3 className="text-xl font-semibold flex items-center gap-2">
                            <CheckSquare className="h-5 w-5" /> All Tasks
                        </h3>
                        <div className="grid gap-2">
                            {tasks?.length > 0 ? tasks.map((task: any, i: number) => (
                                <div key={i} className="p-3 border rounded-lg bg-card flex items-center gap-3">
                                    <div className="h-2 w-2 rounded-full bg-primary shrink-0" />
                                    <span>{task.description || task}</span>
                                </div>
                            )) : <p className="text-muted-foreground">No tasks found.</p>}
                        </div>
                    </section>

                </div>
            </div>
        </div>
    )
}
