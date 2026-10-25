"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { Overview } from "@/components/overview"
import { Scheduler } from "@/components/scheduler"
import { CallControls } from "@/components/call-controls"
import { TaskHistory } from "@/components/task-history"
import {
  ExternalLink,
  Settings as SettingsIcon,
  ShieldCheck,
  PhoneCall
} from "lucide-react"

export default function Home() {
  const [activeTab, setActiveTab] = useState("overview")
  const [agentVoice, setAgentVoice] = useState("alloy")
  const [riskProfile, setRiskProfile] = useState("standard")
  const [maxDuration, setMaxDuration] = useState("600")

  return (
    <div className="flex min-h-screen bg-[#070a12] text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Navbar */}
        <header className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold tracking-tight text-white flex items-center gap-2">
              <PhoneCall className="w-5 h-5 text-indigo-400" />
              AI Voice Agent & Reminder Center
            </h1>
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[11px] font-mono text-indigo-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>FastAPI Backend Active</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-mono text-slate-300 transition"
            >
              <span>API Docs</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>

            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 p-[1px]">
              <div className="w-full h-full rounded-full bg-slate-950 flex items-center justify-center text-xs font-bold text-white">
                AI
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Canvas */}
        <div className="p-6 md:p-8 max-w-7xl w-full mx-auto space-y-8">
          {/* Section 1: Overview */}
          <section id="overview" className="scroll-mt-20">
            <Overview />
          </section>

          {/* Section 2: Schedule Reminders & Calls (Requested by User) */}
          <section id="schedule" className="scroll-mt-20">
            <Scheduler />
          </section>

          {/* Section 3: Call Controls (Direct Immediate Calling) */}
          <section id="calls" className="scroll-mt-20">
            <CallControls />
          </section>

          {/* Section 4: Task History & Executed Reminders */}
          <section id="tasks" className="scroll-mt-20">
            <TaskHistory />
          </section>

          {/* Section 5: Voice & Risk Policy Settings */}
          <section id="settings" className="scroll-mt-20">
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                <div>
                  <h2 className="text-base font-semibold text-white flex items-center gap-2">
                    <SettingsIcon className="w-5 h-5 text-indigo-400" />
                    Agent Voice & Behavior Settings
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Customize voice timbre, task confirmation policies, and call duration limits.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Voice Model Selection */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <label className="block text-xs font-mono uppercase tracking-wider text-slate-300">
                    Voice Persona
                  </label>
                  <select
                    value={agentVoice}
                    onChange={(e) => setAgentVoice(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="alloy">Alloy (Neutral, Balanced)</option>
                    <option value="echo">Echo (Authoritative, Clear)</option>
                    <option value="shimmer">Shimmer (Friendly, Professional)</option>
                    <option value="nova">Nova (Natural, Conversational)</option>
                    <option value="onyx">Onyx (Deep, Formal)</option>
                  </select>
                  <p className="text-[11px] text-slate-500">
                    Neural voice used during speech synthesis.
                  </p>
                </div>

                {/* Risk & Authorization Policy */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <label className="block text-xs font-mono uppercase tracking-wider text-slate-300">
                    Task Execution Permission
                  </label>
                  <select
                    value={riskProfile}
                    onChange={(e) => setRiskProfile(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="autonomous">Autonomous (Executes tasks directly)</option>
                    <option value="standard">Standard (Asks before high-risk actions)</option>
                    <option value="strict">Strict (Requires confirmation for everything)</option>
                  </select>
                  <p className="text-[11px] text-slate-500">
                    Controls whether the agent confirms before executing actions.
                  </p>
                </div>

                {/* Timeout Limit */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <label className="block text-xs font-mono uppercase tracking-wider text-slate-300">
                    Max Call Cutoff (Seconds)
                  </label>
                  <input
                    type="number"
                    value={maxDuration}
                    onChange={(e) => setMaxDuration(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                  <p className="text-[11px] text-slate-500">
                    Auto-disconnect safety cutoff.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Footer */}
          <footer className="pt-6 pb-12 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
            <p>AI Voice Agent Dashboard • Next.js & FastAPI Autonomous Pipeline</p>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span>Ready to schedule & execute</span>
              </span>
            </div>
          </footer>
        </div>
      </main>
    </div>
  )
}
