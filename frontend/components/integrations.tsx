"use client"

import { Mail, Calendar, Check, AlertCircle, ExternalLink, Zap, ShieldCheck } from "lucide-react"
import { useEffect, useState } from "react"

interface IntegrationItem {
  id: string
  name: string
  type: string
  description: string
  icon: React.ElementType
  status: "connected" | "mock" | "disconnected"
  actionText: string
}

const DEFAULT_INTEGRATIONS: IntegrationItem[] = [
  {
    id: "gmail",
    name: "Google Gmail",
    type: "OAuth 2.0",
    description: "Read, search, and draft emails during voice conversation.",
    icon: Mail,
    status: "mock",
    actionText: "Connect Gmail",
  },
  {
    id: "calendar",
    name: "Google Calendar",
    type: "OAuth 2.0",
    description: "Check schedule conflicts, book appointments, and send invites.",
    icon: Calendar,
    status: "mock",
    actionText: "Connect Calendar",
  },
  {
    id: "telephony",
    name: "Twilio Voice Trunk",
    type: "Telephony Provider",
    description: "Programmable SIP trunking for worldwide carrier termination.",
    icon: Zap,
    status: "mock",
    actionText: "View Twilio Config",
  },
]

export function Integrations() {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>(DEFAULT_INTEGRATIONS)
  const [connecting, setConnecting] = useState<string | null>(null)

  const handleConnect = async (item: IntegrationItem) => {
    setConnecting(item.id)
    try {
      if (item.id === "gmail" || item.id === "calendar") {
        const res = await fetch("/api/v1/auth/google/oauth/start")
        if (res.ok) {
          const data = await res.json()
          if (data.authorization_url) {
            window.open(data.authorization_url, "_blank")
          }
        } else {
          // Alert user that OAuth keys need to be in .env
          alert("To connect real Google OAuth, fill GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in .env. Currently running in safe mock mode.")
        }
      } else {
        alert("Twilio credentials can be configured in your .env file (TELEPHONY_ACCOUNT_ID, TELEPHONY_AUTH_SECRET).")
      }
    } catch {
      alert("Running in local mock mode.")
    } finally {
      setConnecting(null)
    }
  }

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            Integrations & Service Connectors
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            External tools the autonomous agent can invoke with risk-based authorization.
          </p>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          <span>OAuth & Credential Vault</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {integrations.map((item) => {
          const Icon = item.icon
          return (
            <div
              key={item.id}
              className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="w-9 h-9 rounded-xl bg-slate-800/80 border border-slate-700/80 flex items-center justify-center text-slate-200">
                    <Icon className="w-4 h-4 text-indigo-400" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-950/60 text-amber-300 border border-amber-500/30">
                    Mock Dev Ready
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-white">{item.name}</h3>
                <p className="text-[10px] text-slate-400 font-mono mt-0.5">{item.type}</p>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <button
                onClick={() => handleConnect(item)}
                disabled={connecting === item.id}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-xs font-medium text-slate-200 transition"
              >
                <span>{item.actionText}</span>
                <ExternalLink className="w-3 h-3 text-slate-400" />
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
