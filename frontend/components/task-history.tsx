"use client"

import { 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  RefreshCw, 
  ChevronRight, 
  Check, 
  Sparkles,
  Layers,
  ShieldCheck
} from "lucide-react"
import { useEffect, useState } from "react"

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  PENDING: { label: "Pending", color: "text-amber-400 bg-amber-950/60 border-amber-500/30", icon: Clock },
  PLANNING: { label: "Planning", color: "text-indigo-400 bg-indigo-950/60 border-indigo-500/30", icon: Sparkles },
  AWAITING_APPROVAL: { label: "Approval Required", color: "text-amber-300 bg-amber-950/70 border-amber-400/40", icon: AlertTriangle },
  RUNNING: { label: "Running", color: "text-cyan-400 bg-cyan-950/60 border-cyan-500/30", icon: RefreshCw },
  VERIFYING: { label: "Verifying Result", color: "text-purple-400 bg-purple-950/60 border-purple-500/30", icon: ShieldCheck },
  COMPLETED: { label: "Completed", color: "text-emerald-400 bg-emerald-950/60 border-emerald-500/30", icon: CheckCircle2 },
  FAILED: { label: "Failed", color: "text-rose-400 bg-rose-950/60 border-rose-500/30", icon: AlertTriangle },
  CANCELLED: { label: "Cancelled", color: "text-slate-400 bg-slate-900 border-slate-700", icon: AlertTriangle },
}

export function TaskHistory() {
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  async function loadTasks() {
    setRefreshing(true)
    try {
      const res = await fetch("/api/v1/tasks/")
      if (res.ok) {
        const data = await res.json()
        setTasks(Array.isArray(data) ? data : [])
      }
    } catch {
      // Offline fallback
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadTasks()
  }, [])

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            Autonomous Task Execution Log
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit history of multi-step tools, verification results, and agent task lifecycle.
          </p>
        </div>

        <button
          onClick={loadTasks}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-mono text-slate-300 border border-slate-700/80 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-cyan-400" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading ? (
        <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-2">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span className="text-xs font-mono">Syncing task state machine...</span>
        </div>
      ) : tasks.length === 0 ? (
        <div className="py-10 text-center rounded-xl bg-slate-950/40 border border-slate-800/60 p-6 space-y-2">
          <Layers className="w-8 h-8 text-slate-600 mx-auto" />
          <h3 className="text-sm font-medium text-slate-300">No tasks in the execution queue yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Once you trigger an outbound call or submit an autonomous instruction, the state machine will log execution steps here.
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-800/80 overflow-hidden bg-slate-950/40">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800/90 bg-slate-900/80 text-slate-400 font-mono uppercase tracking-wider text-[10px]">
                  <th className="px-4 py-3">Task Goal</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Result / Verification</th>
                  <th className="px-4 py-3 text-right">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {tasks.map((task) => {
                  const statusInfo = STATUS_CONFIG[task.status] || {
                    label: task.status,
                    color: "text-slate-400 bg-slate-900 border-slate-700",
                    icon: Clock,
                  }
                  const Icon = statusInfo.icon

                  return (
                    <tr key={task.id} className="hover:bg-slate-900/40 transition">
                      <td className="px-4 py-3 text-slate-200 font-medium max-w-xs truncate">
                        {task.goal}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${statusInfo.color}`}>
                          <Icon className="w-3 h-3" />
                          <span>{statusInfo.label}</span>
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400 max-w-sm truncate font-mono text-[11px]">
                        {task.result_summary || "In progress / awaiting tool output"}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-500 font-mono text-[10px]">
                        {task.created_at ? new Date(task.created_at).toLocaleTimeString() : "Just now"}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
