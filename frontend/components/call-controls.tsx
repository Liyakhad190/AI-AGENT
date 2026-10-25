"use client"

import { useState, useEffect, useRef } from "react"
import { 
  Phone, 
  PhoneCall, 
  PhoneOff, 
  RefreshCw, 
  Volume2, 
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Info,
  Mic,
  Sparkles
} from "lucide-react"

export function CallControls() {
  const [status, setStatus] = useState<string>("idle")
  const [callId, setCallId] = useState<string | null>(null)
  const [phoneNumber, setPhoneNumber] = useState<string>("")
  const [goal, setGoal] = useState<string>("Call to remind me about today's tasks and ask if I need help rescheduling anything.")
  const [callDuration, setCallDuration] = useState<number>(0)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [showRealPhoneHelp, setShowRealPhoneHelp] = useState<boolean>(false)
  const [logHistory, setLogHistory] = useState<string[]>([
    "Telephony adapter ready in Mock mode.",
    "Webhooks configured on /api/v1/calls/webhook."
  ])

  const timerRef = useRef<NodeJS.Timeout | null>(null)

  // Call duration counter
  useEffect(() => {
    if (status === "calling" || status === "in_progress") {
      timerRef.current = setInterval(() => {
        setCallDuration((prev) => prev + 1)
      }, 1000)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
      setCallDuration(0)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [status])

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60)
    const s = sec % 60
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`
  }

  const addLog = (msg: string) => {
    setLogHistory((prev) => [
      `[${new Date().toLocaleTimeString()}] ${msg}`,
      ...prev.slice(0, 15),
    ])
  }

  const callNow = async () => {
    setErrorMessage(null)
    setStatus("initiating")
    addLog(`Initiating dispatch to ${phoneNumber}...`)

    try {
      const res = await fetch("/api/v1/calls/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_number: phoneNumber,
          goal: goal,
        }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Failed to dispatch call" }))
        throw new Error(err.detail || "Dispatch request rejected")
      }

      const data = await res.json()
      const newCallId = data.call_id ?? `call-${Date.now().toString().slice(-6)}`
      setCallId(newCallId)
      setStatus("in_progress")
      addLog(`Call active (ID: ${newCallId}). Session linked to state machine.`)
      pollStatus(newCallId)
    } catch (e: any) {
      setErrorMessage(e.message || "Failed to initiate call")
      setStatus("failed")
      addLog(`Dispatch error: ${e.message}`)
    }
  }

  const endCall = async () => {
    if (!callId) {
      setStatus("idle")
      return
    }
    addLog(`Terminating call ${callId}...`)
    try {
      await fetch(`/api/v1/calls/${callId}/terminate`, { method: "POST" })
    } catch {}
    setStatus("idle")
    setCallId(null)
    addLog("Call ended gracefully.")
  }

  const pollStatus = async (id: string | undefined) => {
    if (!id) return
    for (let i = 0; i < 20; i++) {
      await new Promise((r) => setTimeout(r, 1200))
      try {
        const res = await fetch(`/api/v1/calls/${id}/status`)
        if (res.ok) {
          const data = await res.json()
          if (data.status) {
            setStatus(data.status)
            if (["completed", "failed", "busy", "no-answer"].includes(data.status)) {
              addLog(`Call reached terminal status: ${data.status}`)
              break
            }
          }
        }
      } catch {}
    }
  }

  const isCallActive = status === "initiating" || status === "calling" || status === "in_progress"

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <PhoneCall className="w-5 h-5 text-indigo-400" />
            Immediate Outbound Voice Dispatcher
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Trigger a call right now to ask for reminders, give verbal instructions, or test tasks.
          </p>
        </div>

        {/* Live Call Duration / Status Badge */}
        <div className="flex items-center gap-2">
          {isCallActive ? (
            <div className="flex items-center gap-3 px-3 py-1.5 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-emerald-300">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-mono font-medium">{formatSeconds(callDuration)}</span>
              <span className="text-[11px] uppercase tracking-wider font-mono bg-emerald-500/20 px-1.5 py-0.5 rounded">
                Live Call
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-slate-500"></span>
              <span>Ready</span>
            </div>
          )}
        </div>
      </div>

      {/* Explanatory Collapsible: Why didn't real phone ring? */}
      <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 overflow-hidden">
        <button
          type="button"
          onClick={() => setShowRealPhoneHelp(!showRealPhoneHelp)}
          className="w-full px-4 py-3 flex items-center justify-between text-left text-xs font-medium text-indigo-200 hover:bg-indigo-950/30 transition"
        >
          <span className="flex items-center gap-2">
            <Info className="w-4 h-4 text-cyan-400" />
            <span>Why did my phone not ring? (Mock Mode vs Real Phone Calling)</span>
          </span>
          {showRealPhoneHelp ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showRealPhoneHelp && (
          <div className="px-4 pb-4 pt-1 text-xs text-slate-300 space-y-2 border-t border-indigo-500/10 bg-slate-950/40">
            <p>
              Right now the system is running in <strong className="text-cyan-300">Mock Mode</strong>. In mock mode, the software simulates the call, AI voice conversation, and tasks safely on your screen without charging fees.
            </p>
            <p>
              <strong>To make your physical phone {phoneNumber ? `(${phoneNumber})` : ""} actually ring:</strong> A computer needs a cellular carrier trunk (such as Twilio). Twilio offers free trial numbers. Once you create a Twilio account, set <code className="bg-slate-900 text-indigo-300 px-1.5 py-0.5 rounded">TELEPHONY_PROVIDER=twilio</code> and paste your Twilio credentials in your <code className="bg-slate-900 text-indigo-300 px-1.5 py-0.5 rounded">.env</code> file.
            </p>
          </div>
        )}
      </div>

      {/* Main Grid: Call Setup + Audio Wave / Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Form Controls */}
        <div className="lg:col-span-7 space-y-4">
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
              Destination Phone Number
            </label>
            <div className="relative">
              <Phone className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                disabled={isCallActive}
                placeholder="+91 ..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-60 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
              Reminder Prompt & What To Ask / Do
            </label>
            <textarea
              rows={2}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              disabled={isCallActive}
              placeholder="What reminder should the agent give, and what should it do?"
              className="w-full px-3.5 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-60 transition resize-none"
            />
          </div>

          {/* Action Buttons */}
          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={callNow}
              disabled={isCallActive}
              className={`flex-1 min-w-[160px] flex items-center justify-center gap-2.5 px-5 py-3 rounded-xl text-sm font-semibold shadow-lg transition-all ${
                isCallActive
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                  : "bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white shadow-indigo-500/25 border border-indigo-400/30 hover:scale-[1.01]"
              }`}
            >
              {status === "initiating" ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  <span>Connecting Trunk...</span>
                </>
              ) : (
                <>
                  <PhoneCall className="w-4 h-4 text-white" />
                  <span>Call Right Now</span>
                </>
              )}
            </button>

            <button
              onClick={endCall}
              disabled={!isCallActive}
              className={`flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all ${
                !isCallActive
                  ? "bg-slate-900 text-slate-600 border border-slate-800/80 cursor-not-allowed"
                  : "bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white shadow-lg shadow-rose-950/40 border border-rose-500/30 hover:scale-[1.01]"
              }`}
            >
              <PhoneOff className="w-4 h-4" />
              <span>Hang Up</span>
            </button>
          </div>

          {errorMessage && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Right Column: Audio Waveform Visualizer & Console Log */}
        <div className="lg:col-span-5 flex flex-col justify-between p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Volume2 className="w-3.5 h-3.5 text-indigo-400" /> Speech Stream
              </span>
              <span className="text-[10px] font-mono text-cyan-400">
                {isCallActive ? "Connected" : "Idle"}
              </span>
            </div>

            {/* Simulated Animated Waveform */}
            <div className="h-16 flex items-center justify-center gap-1.5 px-4 bg-slate-900/60 rounded-xl border border-slate-800/60 overflow-hidden">
              {isCallActive ? (
                <>
                  <div className="w-1.5 bg-indigo-500 rounded-full animate-wave-1"></div>
                  <div className="w-1.5 bg-cyan-400 rounded-full animate-wave-2"></div>
                  <div className="w-1.5 bg-indigo-400 rounded-full animate-wave-3"></div>
                  <div className="w-1.5 bg-purple-500 rounded-full animate-wave-4"></div>
                  <div className="w-1.5 bg-cyan-300 rounded-full animate-wave-5"></div>
                  <div className="w-1.5 bg-indigo-500 rounded-full animate-wave-2"></div>
                  <div className="w-1.5 bg-cyan-400 rounded-full animate-wave-1"></div>
                  <div className="w-1.5 bg-indigo-300 rounded-full animate-wave-4"></div>
                  <div className="w-1.5 bg-purple-400 rounded-full animate-wave-3"></div>
                  <div className="w-1.5 bg-cyan-400 rounded-full animate-wave-5"></div>
                </>
              ) : (
                <div className="text-xs text-slate-500 flex items-center gap-2 font-mono">
                  <Mic className="w-3.5 h-3.5 text-slate-600" />
                  <span>Awaiting call initiation...</span>
                </div>
              )}
            </div>
          </div>

          {/* Telephony Event Stream */}
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block mb-1.5">
              Live Call Telemetry
            </span>
            <div className="h-28 overflow-y-auto p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono text-slate-300 space-y-1">
              {logHistory.map((item, idx) => (
                <div key={idx} className="leading-snug text-slate-300/90 truncate">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
