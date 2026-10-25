"use client"

import { useState, useEffect } from "react"
import { 
  Calendar, 
  Clock, 
  Phone, 
  Send, 
  Trash2, 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw,
  BellRing,
  Sparkles
} from "lucide-react"

export function Scheduler() {
  const [phoneNumber, setPhoneNumber] = useState("")
  const [reminderDate, setReminderDate] = useState("")
  const [reminderTime, setReminderTime] = useState("")
  const [reminderPrompt, setReminderPrompt] = useState("Call me to remind me to take medication and ask if I have completed my morning tasks.")
  const [scheduledJobs, setScheduledJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [actionMessage, setActionMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  // Default date to tomorrow and time to 09:00 AM
  useEffect(() => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const yyyy = tomorrow.getFullYear()
    const mm = String(tomorrow.getMonth() + 1).padStart(2, "0")
    const dd = String(tomorrow.getDate()).padStart(2, "0")
    setReminderDate(`${yyyy}-${mm}-${dd}`)
    setReminderTime("09:00")
    loadScheduledJobs()
  }, [])

  async function loadScheduledJobs() {
    setLoading(true)
    try {
      const res = await fetch("/api/v1/schedule/")
      if (res.ok) {
        const data = await res.json()
        setScheduledJobs(Array.isArray(data) ? data : [])
      }
    } catch {
      // Offline fallback
    } finally {
      setLoading(false)
    }
  }

  const handleSchedule = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!reminderDate || !reminderTime || !reminderPrompt || !phoneNumber) {
      setActionMessage({ type: "error", text: "Please fill in all date, time, phone, and reminder fields." })
      return
    }

    setSubmitting(true)
    setActionMessage(null)

    try {
      const scheduledDateTime = new Date(`${reminderDate}T${reminderTime}:00`).toISOString()
      const res = await fetch("/api/v1/schedule/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: phoneNumber,
          reminder_text: reminderPrompt,
          scheduled_time: scheduledDateTime,
        }),
      })

      if (!res.ok) {
        throw new Error("Failed to schedule call")
      }

      setActionMessage({
        type: "success",
        text: `Call successfully scheduled for ${reminderDate} at ${reminderTime}! The agent will automatically call and execute the reminder.`,
      })
      loadScheduledJobs()
    } catch (err: any) {
      setActionMessage({ type: "error", text: err.message || "Could not schedule call" })
    } finally {
      setSubmitting(false)
    }
  }

  const handleTriggerNow = async (id: string) => {
    try {
      setActionMessage({ type: "success", text: "Triggering call and task right now..." })
      const res = await fetch(`/api/v1/schedule/${id}/trigger`, { method: "POST" })
      if (res.ok) {
        setActionMessage({ type: "success", text: "Call dispatched! Task and call session initiated." })
        loadScheduledJobs()
      }
    } catch {
      setActionMessage({ type: "error", text: "Failed to trigger call." })
    }
  }

  const handleCancel = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/schedule/${id}`, { method: "DELETE" })
      if (res.ok) {
        loadScheduledJobs()
      }
    } catch {
      // Fallback
    }
  }

  const activeJobs = scheduledJobs.filter((j) => j.is_active)
  const pastJobs = scheduledJobs.filter((j) => !j.is_active)

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <BellRing className="w-5 h-5 text-indigo-400" />
            Scheduled Reminder & Task Calling
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Set a future date, day, or time for the autonomous agent to call you, ask questions, or execute reminders.
          </p>
        </div>

        <button
          onClick={loadScheduledJobs}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-mono text-slate-300 border border-slate-800 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {actionMessage && (
        <div
          className={`p-3.5 rounded-xl text-xs flex items-center gap-2.5 border ${
            actionMessage.type === "success"
              ? "bg-emerald-950/60 border-emerald-500/30 text-emerald-300"
              : "bg-rose-950/60 border-rose-500/30 text-rose-300"
          }`}
        >
          {actionMessage.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          )}
          <span>{actionMessage.text}</span>
        </div>
      )}

      {/* Scheduler Form */}
      <form onSubmit={handleSchedule} className="grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* Phone input */}
        <div className="md:col-span-4">
          <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
            Phone Number
          </label>
          <div className="relative">
            <Phone className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+91 ..."
              className="w-full pl-9 pr-3 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Date picker */}
        <div className="md:col-span-4">
          <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
            Schedule Date
          </label>
          <div className="relative">
            <Calendar className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
            <input
              type="date"
              value={reminderDate}
              onChange={(e) => setReminderDate(e.target.value)}
              className="w-full pl-9 pr-3 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Time picker */}
        <div className="md:col-span-4">
          <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
            Schedule Time
          </label>
          <div className="relative">
            <Clock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
            <input
              type="time"
              value={reminderTime}
              onChange={(e) => setReminderTime(e.target.value)}
              className="w-full pl-9 pr-3 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Reminder text & prompt */}
        <div className="md:col-span-12">
          <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
            Reminder Message & What The Agent Should Do When You Answer
          </label>
          <textarea
            rows={2}
            value={reminderPrompt}
            onChange={(e) => setReminderPrompt(e.target.value)}
            placeholder="e.g. Remind me to send the status report to the team, ask if it's done, and log the response"
            className="w-full px-3.5 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none"
          />
        </div>

        {/* Submit Button */}
        <div className="md:col-span-12 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-sm font-semibold shadow-lg shadow-indigo-500/20 transition disabled:opacity-50"
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Scheduling...</span>
              </>
            ) : (
              <>
                <Calendar className="w-4 h-4" />
                <span>Schedule Reminder Call</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Scheduled Queue List */}
      <div className="space-y-3 pt-4 border-t border-slate-800/80">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <span>Active Scheduled Calls Queue</span>
          <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 text-[10px]">
            {activeJobs.length} Pending
          </span>
        </h3>

        {activeJobs.length === 0 ? (
          <div className="p-6 text-center rounded-xl bg-slate-950/40 border border-slate-800/60 text-xs text-slate-400">
            No reminder calls scheduled right now. Use the form above to schedule a call for any date or time!
          </div>
        ) : (
          <div className="space-y-2">
            {activeJobs.map((job) => {
              const payload = job.payload || {}
              const scheduledDate = job.run_at ? new Date(job.run_at).toLocaleString() : "Upcoming"

              return (
                <div
                  key={job.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700/80 transition"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono text-[11px] flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {scheduledDate}
                      </span>
                      <span className="font-mono text-xs text-slate-300">
                        {payload.to_number || "+91 ..."}
                      </span>
                    </div>
                    <p className="text-xs text-slate-200 font-medium">
                      {payload.reminder_text}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    <button
                      type="button"
                      onClick={() => handleTriggerNow(job.id)}
                      title="Trigger and test this call immediately"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-medium transition"
                    >
                      <Play className="w-3.5 h-3.5" />
                      <span>Trigger Now</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleCancel(job.id)}
                      title="Cancel this reminder"
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950/60 text-slate-400 hover:text-rose-300 border border-slate-700 hover:border-rose-500/30 transition"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
