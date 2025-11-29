"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, MessageSquare, History, Home, Settings, X } from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
    { name: "Home", href: "/", icon: Home },
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Chat", href: "/chat", icon: MessageSquare },
    { name: "History", href: "/history", icon: History },
]

export function Sidebar() {
    const pathname = usePathname()
    const [showSettings, setShowSettings] = useState(false)
    const [apiKey, setApiKey] = useState("")

    const saveApiKey = async () => {
        if (apiKey.length > 10) {
            try {
                const res = await fetch('http://localhost:8000/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: apiKey })
                })
                if (res.ok) {
                    alert('API Key saved successfully!')
                    setShowSettings(false)
                } else {
                    alert('Failed to save API Key')
                }
            } catch (error) {
                console.error(error)
                alert('Error saving API Key')
            }
        } else {
            alert('Please enter a valid API Key')
        }
    }

    return (
        <>
            <div className="flex h-full w-64 flex-col border-r bg-background">
                <div className="flex h-14 items-center border-b px-4">
                    <Link href="/" className="flex items-center gap-2 font-semibold">
                        <span className="text-xl">ScholarFlow AI</span>
                    </Link>
                </div>
                <div className="flex-1 overflow-auto py-2">
                    <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
                        {navigation.map((item) => {
                            const Icon = item.icon
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary",
                                        pathname === item.href
                                            ? "bg-muted text-primary"
                                            : "text-muted-foreground"
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    {item.name}
                                </Link>
                            )
                        })}
                    </nav>
                </div>
                <div className="mt-auto p-4 border-t">
                    <button
                        onClick={() => setShowSettings(true)}
                        className="flex items-center gap-3 px-2 py-2 text-sm font-medium text-muted-foreground hover:text-primary transition-colors w-full text-left rounded-md hover:bg-muted"
                    >
                        <Settings className="h-4 w-4" />
                        <span>Settings</span>
                    </button>
                </div>
            </div>

            {/* Settings Modal */}
            {showSettings && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="bg-background p-6 rounded-lg shadow-lg w-96 border animate-in fade-in zoom-in duration-200">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold">Settings</h3>
                            <button onClick={() => setShowSettings(false)} className="text-muted-foreground hover:text-foreground">
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Google API Key</label>
                                <input
                                    type="password"
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="Enter your Gemini API Key"
                                    className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                                />
                                <p className="text-xs text-muted-foreground">
                                    Required for AI features. Key is stored in backend memory.
                                </p>
                            </div>
                            <button
                                onClick={saveApiKey}
                                className="w-full py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 font-medium transition-colors"
                            >
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
