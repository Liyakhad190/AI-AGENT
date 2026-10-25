"use client"

import { usePathname } from "next/navigation"
import { useState } from "react"
import { 
  Phone, 
  List, 
  Bell, 
  Settings, 
  Radio, 
  Bot, 
  ShieldCheck, 
  Menu, 
  X, 
  Activity,
  Zap,
  CalendarClock
} from "lucide-react"

interface SectionItem {
  id: string
  label: string
  icon: React.ElementType
  badge?: string
}

const NAV_ITEMS: SectionItem[] = [
  { id: "overview", label: "Live Overview", icon: Activity },
  { id: "schedule", label: "Schedule Reminders", icon: CalendarClock, badge: "Scheduler" },
  { id: "calls", label: "Direct Call Now", icon: Phone },
  { id: "tasks", label: "Executed Tasks & History", icon: List },
  { id: "settings", label: "Voice Settings", icon: Settings },
]

export function Sidebar({ activeTab, setActiveTab }: { activeTab?: string; setActiveTab?: (id: string) => void }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const currentTab = activeTab || "overview"

  const handleSelect = (id: string) => {
    if (setActiveTab) {
      setActiveTab(id)
    } else {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: "smooth" })
    }
    setMobileOpen(false)
  }

  return (
    <>
      {/* Mobile Top Bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 flex items-center justify-between px-4 py-3 bg-slate-950/90 backdrop-blur-md border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-bold text-sm">
            AI
          </div>
          <span className="font-semibold text-slate-100 tracking-tight text-base">VoiceAgent OS</span>
        </div>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Backdrop for mobile */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/70 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-50 md:z-20 h-screen w-72 shrink-0 flex flex-col border-r border-slate-800/80 bg-slate-950/95 backdrop-blur-2xl transition-transform duration-300 ease-out ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="flex h-full flex-col justify-between p-4">
          <div>
            {/* Logo / Header */}
            <div className="flex items-center justify-between px-2 py-4 mb-4 border-b border-slate-800/60">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/30 text-white font-bold text-sm">
                    <Bot className="w-5 h-5" />
                  </div>
                  <span className="absolute -top-1 -right-1 flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                </div>
                <div>
                  <h1 className="font-semibold text-slate-100 tracking-tight text-base leading-none">VoiceAgent</h1>
                  <span className="text-[11px] text-indigo-400 font-mono tracking-wider uppercase font-medium">Autonomous v0.1</span>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="space-y-1.5">
              <div className="px-3 py-1 text-[11px] font-semibold text-slate-500 uppercase tracking-wider font-mono">
                System Console
              </div>
              {NAV_ITEMS.map((item) => {
                const Icon = item.icon
                const isActive = currentTab === item.id
                return (
                  <button
                    key={item.id}
                    onClick={() => handleSelect(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                      isActive
                        ? "bg-gradient-to-r from-indigo-600/20 to-indigo-900/10 text-white border border-indigo-500/30 shadow-sm shadow-indigo-950/50"
                        : "text-slate-400 hover:text-slate-100 hover:bg-slate-900/60 border border-transparent"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 transition ${isActive ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-200"}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                        {item.badge}
                      </span>
                    )}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Footer Telephony Status Badge */}
          <div className="space-y-3 pt-4 border-t border-slate-800/60">
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" /> Security State
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  DEV MOCK
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Running in safe sandbox mode. No real telephony or toll charges incurred.
              </p>
            </div>
            
            <div className="flex items-center justify-between px-2 text-xs text-slate-500 font-mono">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Backend :8000
              </span>
              <span>FastAPI</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
