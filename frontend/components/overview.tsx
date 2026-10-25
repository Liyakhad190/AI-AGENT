"use client"

import { useEffect, useState } from "react"
import { Phone, Bot, CheckCircle2, CalendarClock, ListTodo, Sparkles } from "lucide-react"

export function Overview() {
  const [taskCount, setTaskCount] = useState<number | null>(null)
  const [scheduledCount, setScheduledCount] = useState<number | null>(null)

  useEffect(() => {
    async function loadStats() {
      try {
        const [taskRes, schedRes] = await Promise.all([
          fetch("/api/v1/tasks/"),
          fetch("/api/v1/schedule/"),
        ])
        if (taskRes.ok) {
          const tasks = await taskRes.json()
          setTaskCount(Array.isArray(tasks) ? tasks.length : 0)
        }
        if (schedRes.ok) {
          const scheds = await schedRes.json()
          const activeScheds = Array.isArray(scheds) ? scheds.filter((s: any) => s.is_active) : []
          setScheduledCount(activeScheds.length)
        }
      } catch {
        // Fallback
      }
    }
    loadStats()
  }, [])

  return (
    <div className="space-y-4">
      {/* Metric Cards Grid - Cleaned up (No confusing budget) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Agent Core */}
        <div className="glass-panel-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl group-hover:bg-indigo-500/20 transition-all duration-500"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Agent Core</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">Active</span>
            <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" /> 100% Ready
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400">FastAPI Autonomous Engine</p>
        </div>

        {/* Card 2: Voice Calls */}
        <div className="glass-panel-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all duration-500"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Voice Dispatch</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Phone className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">Ready</span>
            <span className="text-xs text-cyan-400">Outbound calling</span>
          </div>
          <p className="mt-1 text-xs text-slate-400">Instant or Scheduled</p>
        </div>

        {/* Card 3: Scheduled Reminders */}
        <div className="glass-panel-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl group-hover:bg-purple-500/20 transition-all duration-500"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Scheduled Reminders</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <CalendarClock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">
              {scheduledCount !== null ? scheduledCount : 0}
            </span>
            <span className="text-xs text-slate-400">pending calls</span>
          </div>
          <p className="mt-1 text-xs text-slate-400">Auto-dispatches on time</p>
        </div>

        {/* Card 4: Executed Tasks */}
        <div className="glass-panel-interactive p-5 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-all duration-500"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Tasks Completed</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <ListTodo className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">
              {taskCount !== null ? taskCount : 0}
            </span>
            <span className="text-xs text-slate-400">recorded</span>
          </div>
          <p className="mt-1 text-xs text-slate-400">Autonomous state machine</p>
        </div>
      </div>
    </div>
  )
}
