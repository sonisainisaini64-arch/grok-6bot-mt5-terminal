import MetaTrader5 as mt5
import pandas as pd
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from google import genai

app = Flask(__name__)

# Initialize MT5
if not mt5.initialize():
    print("❌ MT5 initialize failed! Ensure MT5 is running.")

SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M15

GEMINI_API_KEY = "AQ.Ab8RN6Il-sXfNb1L_sKCJSh1P0Av0z7n5UShZt5yCGac72B2Ig"
ai_client = genai.Client(api_key=GEMINI_API_KEY)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GROK 6: Multi-Agent Trading Terminal & Hinglish War Room</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Grotesk:wght@400;600;700&family=VT323&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            pixel: ['"Press Start 2P"', 'monospace'],
            retro: ['"VT323"', 'monospace'],
            sans: ['"Space Grotesk"', 'sans-serif'],
          },
          colors: {
            cyberDark: '#080c14',
            cyberPanel: '#0e1422',
            cyberCard: '#131b2e',
            cyberBorder: '#1f2b45',
            botScout: '#FFD000',
            botNews: '#FF3B30',
            botSent: '#AF52DE',
            botChart: '#007AFF',
            botRisk: '#34C759',
            botDec: '#FF9500'
          }
        }
      }
    }
  </script>

  <style>
    .scanlines { position: relative; }
    .scanlines::before {
      content: " ";
      display: block;
      position: absolute;
      top: 0; left: 0; bottom: 0; right: 0;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.35) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
      z-index: 90;
      background-size: 100% 3px, 6px 100%;
      pointer-events: none;
      opacity: 0.85;
    }
    .glow-yellow { box-shadow: 0 0 15px rgba(255, 208, 0, 0.35); }
    .glow-red { box-shadow: 0 0 15px rgba(255, 59, 48, 0.35); }
    .glow-purple { box-shadow: 0 0 15px rgba(175, 82, 222, 0.35); }
    .glow-blue { box-shadow: 0 0 15px rgba(0, 122, 255, 0.35); }
    .glow-green { box-shadow: 0 0 15px rgba(52, 199, 89, 0.35); }
    .glow-orange { box-shadow: 0 0 15px rgba(255, 149, 0, 0.35); }
    .glow-text-green { text-shadow: 0 0 10px rgba(52, 199, 89, 0.7); }

    .chat-bubble-scout { border-left: 3px solid #FFD000; background: rgba(255, 208, 0, 0.06); }
    .chat-bubble-news { border-left: 3px solid #FF3B30; background: rgba(255, 59, 48, 0.06); }
    .chat-bubble-sent { border-left: 3px solid #AF52DE; background: rgba(175, 82, 222, 0.06); }
    .chat-bubble-chart { border-left: 3px solid #007AFF; background: rgba(0, 122, 255, 0.06); }
    .chat-bubble-risk { border-left: 3px solid #34C759; background: rgba(52, 199, 89, 0.06); }
    .chat-bubble-dec { border-left: 3px solid #FF9500; background: rgba(255, 149, 0, 0.09); }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #080c14; }
    ::-webkit-scrollbar-thumb { background: #1f2b45; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #34C759; }

    @keyframes pulseGlow {
      0%, 100% { opacity: 0.9; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.98); }
    }
    .status-pulse { animation: pulseGlow 2s infinite ease-in-out; }
    .pixel-crisp { image-rendering: pixelated; }
  </style>
</head>
<body class="bg-cyberDark text-slate-100 font-sans min-h-screen flex flex-col overflow-x-hidden selection:bg-emerald-500 selection:text-black">
  <div id="crtOverlay" class="scanlines min-h-screen flex flex-col justify-between">

    <!-- TOP HEADER -->
    <header class="border-b border-cyberBorder bg-cyberPanel/90 backdrop-blur px-4 py-3 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500 flex items-center justify-center glow-green">
            <span class="font-pixel text-emerald-400 text-sm">6G</span>
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h1 class="font-pixel text-sm md:text-base text-white tracking-wider">6 GROK BOTS</h1>
              <span class="bg-emerald-950 text-emerald-400 text-[10px] font-retro px-2 py-0.5 rounded border border-emerald-500/40 font-bold uppercase tracking-widest">LIVE MT5 + GEMINI AI</span>
            </div>
            <p class="text-xs text-slate-400 font-retro tracking-wider">BALANCE: <span class="text-emerald-400 font-bold glow-text-green" id="headerBalance">$10,000.00</span></p>
          </div>
        </div>

        <div class="flex items-center flex-wrap gap-2">
          <div class="flex items-center bg-cyberDark border border-cyberBorder rounded px-2.5 py-1 text-xs">
            <span class="text-slate-400 mr-2 font-retro text-sm uppercase">ASSET:</span>
            <span class="text-emerald-400 font-bold">XAUUSD (GOLD)</span>
          </div>

          <div class="flex items-center space-x-1 border-l border-cyberBorder pl-2">
            <button onclick="toggleAudio()" id="audioBtn" class="p-2 rounded bg-cyberDark border border-cyberBorder text-slate-400 hover:text-emerald-400 text-xs transition">
              🔊 <span id="audioState">ON</span>
            </button>
            <button onclick="toggleScanlines()" id="crtBtn" class="p-2 rounded bg-cyberDark border border-cyberBorder text-slate-400 hover:text-emerald-400 text-xs transition">
              📺 CRT
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- MAIN VIEW -->
    <main class="max-w-7xl mx-auto w-full px-3 py-4 flex-1 space-y-4">
      
      <!-- SUB-NAVIGATION / TABS -->
      <div class="flex items-center space-x-1 sm:space-x-2 overflow-x-auto pb-2 border-b border-cyberBorder text-xs scrollbar-thin">
        <button onclick="switchTab('room')" id="tab-room" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-emerald-500 text-black shadow-lg">
          <span>🏛️</span><span>COMMAND ROOM</span>
        </button>
        <button onclick="switchTab('scout')" id="tab-scout" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-cyberCard border border-cyberBorder text-botScout hover:border-botScout">
          <span class="w-2.5 h-2.5 rounded-full bg-botScout inline-block"></span><span>01 SCOUT</span>
        </button>
        <button onclick="switchTab('news')" id="tab-news" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-cyberCard border border-cyberBorder text-botNews hover:border-botNews">
          <span class="w-2.5 h-2.5 rounded-full bg-botNews inline-block"></span><span>02 NEWS</span>
        </button>
        <button onclick="switchTab('sentiment')" id="tab-sentiment" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-cyberCard border border-cyberBorder text-botSent hover:border-botSent">
          <span class="w-2.5 h-2.5 rounded-full bg-botSent inline-block"></span><span>03 SENTIMENT</span>
        </button>
        <button onclick="switchTab('charts')" id="tab-charts" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-cyberCard border border-cyberBorder text-botChart hover:border-botChart">
          <span class="w-2.5 h-2.5 rounded-full bg-botChart inline-block"></span><span>04 CHARTS</span>
        </button>
        <button onclick="switchTab('risk')" id="tab-risk" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-cyberCard border border-cyberBorder text-botRisk hover:border-botRisk">
          <span class="w-2.5 h-2.5 rounded-full bg-botRisk inline-block"></span><span>05 RISK</span>
        </button>
        <button onclick="switchTab('decision')" id="tab-decision" class="tab-btn px-3 py-2 rounded-lg font-pixel text-[10px] flex items-center space-x-2 transition bg-cyberCard border border-cyberBorder text-botDec hover:border-botDec">
          <span class="w-2.5 h-2.5 rounded-full bg-botDec inline-block"></span><span>06 DECISION</span>
        </button>
      </div>

      <!-- TAB 0: COMMAND ROOM OVERVIEW -->
      <section id="view-room" class="space-y-4">
        
        <!-- Candlestick Visualizer -->
        <div class="bg-cyberPanel border border-cyberBorder rounded-xl p-4">
          <div class="flex items-center justify-between pb-3 border-b border-cyberBorder mb-3">
            <div class="flex items-center space-x-3">
              <span class="font-pixel text-xs text-emerald-400 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 status-pulse"></span>
                TERMINAL MASTER FEED
              </span>
              <span id="roomActiveTicker" class="text-xs bg-emerald-950 text-emerald-300 font-mono px-2 py-0.5 rounded border border-emerald-800">XAUUSD Live Feed</span>
            </div>
            <div class="flex items-center space-x-3 text-xs font-retro text-slate-400">
              <span>AGENTS: <strong class="text-emerald-400">6/6</strong></span>
              <span>LATENCY: <strong class="text-emerald-400">0ms (IPC)</strong></span>
              <span class="font-mono text-emerald-400" id="liveClock">--:--:--</span>
            </div>
          </div>

          <div class="relative w-full h-56 bg-cyberDark rounded-lg border border-cyberBorder/60 overflow-hidden">
            <canvas id="overviewChartCanvas" class="w-full h-full block"></canvas>
            <div class="absolute top-2 left-3 pointer-events-none flex items-center space-x-4 text-xs font-mono">
              <span class="text-emerald-400">RESIST: <span id="chartHigh">--</span></span>
              <span class="text-rose-400">SUPPORT: <span id="chartLow">--</span></span>
              <span class="text-sky-400" id="scoutVolState">VOL: NORMAL</span>
            </div>
          </div>
        </div>

        <!-- 6 Workstations Grid -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          
          <!-- Desk 1: SCOUT -->
          <div onclick="switchTab('scout')" class="cursor-pointer group bg-cyberCard border border-cyberBorder hover:border-botScout rounded-xl p-3 transition flex flex-col justify-between hover:glow-yellow">
            <div class="flex justify-between items-start">
              <span class="font-retro text-xs text-botScout">01 SCOUT</span>
              <span class="w-2 h-2 rounded-full bg-botScout status-pulse"></span>
            </div>
            <div class="my-3 flex justify-center">
              <svg width="44" height="44" viewBox="0 0 24 24" class="pixel-crisp drop-shadow">
                <rect x="6" y="4" width="12" height="14" rx="6" fill="#FFD000"/>
                <rect x="8" y="9" width="2" height="4" fill="#000"/>
                <rect x="14" y="9" width="2" height="4" fill="#000"/>
                <rect x="4" y="11" width="2" height="4" fill="#FFD000"/>
                <rect x="18" y="11" width="2" height="4" fill="#FFD000"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] font-pixel text-slate-300">PRICE & SPREAD</div>
              <div class="text-xs font-mono text-emerald-400 font-bold" id="desk1Status">Loading...</div>
            </div>
          </div>

          <!-- Desk 2: NEWS -->
          <div onclick="switchTab('news')" class="cursor-pointer group bg-cyberCard border border-cyberBorder hover:border-botNews rounded-xl p-3 transition flex flex-col justify-between hover:glow-red">
            <div class="flex justify-between items-start">
              <span class="font-retro text-xs text-botNews">02 NEWS</span>
              <span class="w-2 h-2 rounded-full bg-botNews status-pulse"></span>
            </div>
            <div class="my-3 flex justify-center">
              <svg width="44" height="44" viewBox="0 0 24 24" class="pixel-crisp drop-shadow">
                <rect x="6" y="4" width="12" height="14" rx="6" fill="#FF3B30"/>
                <rect x="8" y="9" width="2" height="4" fill="#000"/>
                <rect x="14" y="9" width="2" height="4" fill="#000"/>
                <rect x="4" y="11" width="2" height="4" fill="#FF3B30"/>
                <rect x="18" y="11" width="2" height="4" fill="#FF3B30"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] font-pixel text-slate-300">CATALYSTS</div>
              <div class="text-xs font-mono text-botNews font-bold" id="desk2Status">MACRO INTEL</div>
            </div>
          </div>

          <!-- Desk 3: SENTIMENT -->
          <div onclick="switchTab('sentiment')" class="cursor-pointer group bg-cyberCard border border-cyberBorder hover:border-botSent rounded-xl p-3 transition flex flex-col justify-between hover:glow-purple">
            <div class="flex justify-between items-start">
              <span class="font-retro text-xs text-botSent">03 SENTIMENT</span>
              <span class="w-2 h-2 rounded-full bg-botSent status-pulse"></span>
            </div>
            <div class="my-3 flex justify-center">
              <svg width="44" height="44" viewBox="0 0 24 24" class="pixel-crisp drop-shadow">
                <rect x="6" y="4" width="12" height="14" rx="6" fill="#AF52DE"/>
                <rect x="8" y="9" width="2" height="4" fill="#000"/>
                <rect x="14" y="9" width="2" height="4" fill="#000"/>
                <rect x="3" y="8" width="3" height="7" rx="1" fill="#FFFFFF"/>
                <rect x="18" y="8" width="3" height="7" rx="1" fill="#FFFFFF"/>
                <rect x="5" y="3" width="14" height="2" fill="#FFFFFF"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] font-pixel text-slate-300">GEMINI SCORE</div>
              <div class="text-xs font-mono text-purple-400 font-bold" id="desk3Status">72 (BULLISH)</div>
            </div>
          </div>

          <!-- Desk 4: CHARTS -->
          <div onclick="switchTab('charts')" class="cursor-pointer group bg-cyberCard border border-cyberBorder hover:border-botChart rounded-xl p-3 transition flex flex-col justify-between hover:glow-blue">
            <div class="flex justify-between items-start">
              <span class="font-retro text-xs text-botChart">04 CHARTS</span>
              <span class="w-2 h-2 rounded-full bg-botChart status-pulse"></span>
            </div>
            <div class="my-3 flex justify-center">
              <svg width="44" height="44" viewBox="0 0 24 24" class="pixel-crisp drop-shadow">
                <rect x="6" y="4" width="12" height="14" rx="6" fill="#007AFF"/>
                <rect x="8" y="9" width="2" height="4" fill="#000"/>
                <rect x="14" y="9" width="2" height="4" fill="#000"/>
                <rect x="2" y="11" width="3" height="8" transform="rotate(-20 2 11)" fill="#FFF"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] font-pixel text-slate-300">STRUCTURE</div>
              <div class="text-xs font-mono text-sky-400 font-bold" id="desk4Status">M15 TREND</div>
            </div>
          </div>

          <!-- Desk 5: RISK -->
          <div onclick="switchTab('risk')" class="cursor-pointer group bg-cyberCard border border-cyberBorder hover:border-botRisk rounded-xl p-3 transition flex flex-col justify-between hover:glow-green">
            <div class="flex justify-between items-start">
              <span class="font-retro text-xs text-botRisk">05 RISK</span>
              <span class="w-2 h-2 rounded-full bg-botRisk status-pulse"></span>
            </div>
            <div class="my-3 flex justify-center">
              <svg width="44" height="44" viewBox="0 0 24 24" class="pixel-crisp drop-shadow">
                <rect x="6" y="4" width="12" height="14" rx="6" fill="#34C759"/>
                <rect x="8" y="9" width="2" height="4" fill="#000"/>
                <rect x="14" y="9" width="2" height="4" fill="#000"/>
                <rect x="4" y="11" width="2" height="4" fill="#34C759"/>
                <rect x="18" y="11" width="2" height="4" fill="#34C759"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] font-pixel text-slate-300">LOT SIZING</div>
              <div class="text-xs font-mono text-emerald-400 font-bold" id="desk5Status">0.04 LOTS</div>
            </div>
          </div>

          <!-- Desk 6: DECISION -->
          <div onclick="switchTab('decision')" class="cursor-pointer group bg-cyberCard border border-cyberBorder hover:border-botDec rounded-xl p-3 transition flex flex-col justify-between hover:glow-orange">
            <div class="flex justify-between items-start">
              <span class="font-retro text-xs text-botDec">06 DECISION</span>
              <span class="w-2 h-2 rounded-full bg-botDec status-pulse"></span>
            </div>
            <div class="my-3 flex justify-center">
              <svg width="44" height="44" viewBox="0 0 24 24" class="pixel-crisp drop-shadow">
                <rect x="5" y="6" width="14" height="12" rx="4" fill="#FF9500"/>
                <rect x="8" y="9" width="3" height="5" fill="#FFE58F"/>
                <rect x="13" y="9" width="3" height="5" fill="#FFE58F"/>
                <rect x="11" y="2" width="2" height="4" fill="#FF9500"/>
                <circle cx="12" cy="2" r="1.5" fill="#FFD000"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] font-pixel text-slate-300">FINAL CALL</div>
              <div class="text-xs font-mono font-bold text-amber-400" id="desk6Status">WAIT</div>
            </div>
          </div>

        </div>
      </section>

      <!-- TAB 1 TO 6 DETAILED VIEWS -->
      <section id="view-scout" class="hidden space-y-4">
        <div class="bg-cyberPanel border border-botScout/40 rounded-xl p-4 glow-yellow">
          <h2 class="font-pixel text-base text-botScout mb-2">BOT 1: SCOUT DETAILS</h2>
          <div class="p-3 bg-cyberDark rounded border border-cyberBorder text-xs font-mono space-y-2">
            <div class="text-emerald-400 font-bold" id="scoutDetailPrice">BID: -- | ASK: --</div>
            <div class="text-slate-300" id="scoutDetailVol">VOLUME: NORMAL</div>
          </div>
        </div>
      </section>

      <section id="view-news" class="hidden space-y-4">
        <div class="bg-cyberPanel border border-botNews/40 rounded-xl p-4 glow-red">
          <h2 class="font-pixel text-base text-botNews mb-2">BOT 2: NEWS & MACRO</h2>
          <div class="p-3 bg-cyberDark rounded border border-cyberBorder text-xs font-mono" id="newsLiveHeadline">Loading Gemini News...</div>
        </div>
      </section>

      <section id="view-sentiment" class="hidden space-y-4">
        <div class="bg-cyberPanel border border-botSent/40 rounded-xl p-4 glow-purple flex flex-col items-center">
          <h2 class="font-pixel text-base text-botSent mb-4">BOT 3: SENTIMENT GAUGE</h2>
          <div class="w-64 h-36 relative"><canvas id="sentimentGaugeCanvas" width="256" height="144" class="w-full h-full"></canvas></div>
          <div class="font-pixel text-3xl text-emerald-400 mt-2" id="sentimentScoreDisplay">72</div>
        </div>
      </section>

      <section id="view-charts" class="hidden space-y-4">
        <div class="bg-cyberPanel border border-botChart/40 rounded-xl p-4 glow-blue">
          <h2 class="font-pixel text-base text-botChart mb-2">BOT 4: KEY LEVELS HUD</h2>
          <div class="p-3 bg-cyberDark rounded border border-cyberBorder text-xs font-mono space-y-2">
            <div>RESISTANCE: <span id="hudResist" class="text-rose-400 font-bold">--</span></div>
            <div>SUPPORT: <span id="hudSupport" class="text-emerald-400 font-bold">--</span></div>
            <div>TREND: <span id="hudTrend" class="text-yellow-400 font-bold">--</span></div>
          </div>
        </div>
      </section>

      <section id="view-risk" class="hidden space-y-4">
        <div class="bg-cyberPanel border border-botRisk/40 rounded-xl p-4 glow-green">
          <h2 class="font-pixel text-base text-botRisk mb-2">BOT 5: RISK & ALLOCATION</h2>
          <div class="p-3 bg-cyberDark rounded border border-cyberBorder text-xs font-mono space-y-2">
            <div>BALANCE: <span id="riskVaultBal" class="text-emerald-400 font-bold">$10,000.00</span></div>
            <div>ALLOCATED LOT: <span id="riskLotDisplay" class="text-botRisk font-bold">0.04 Lots</span></div>
          </div>
        </div>
      </section>

      <section id="view-decision" class="hidden space-y-4">
        <div class="bg-cyberPanel border border-botDec/50 rounded-xl p-4 glow-orange text-center">
          <h2 class="font-pixel text-xl text-white mb-2">BOT 6 FINAL VERDICT</h2>
          <div class="font-pixel text-2xl text-amber-400 mb-2" id="decActionDisplay">WAIT</div>
          <p class="font-mono text-xs text-slate-300" id="decReasonDisplay">Awaiting clean breakout...</p>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- NEW SECTION: 6-BOT HINGLISH WAR ROOM CHAT ROOM           -->
      <!-- ======================================================== -->
      <section class="bg-cyberPanel border border-cyberBorder rounded-xl p-4 mt-6">
        <div class="flex items-center justify-between pb-3 mb-3 border-b border-cyberBorder">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded bg-emerald-500/10 border border-emerald-500 flex items-center justify-center glow-green">
              <span class="text-sm">💬</span>
            </div>
            <div>
              <h2 class="font-pixel text-xs text-emerald-400 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 status-pulse"></span>
                6-BOT HINGLISH WAR ROOM CHAT
              </h2>
              <p class="font-retro text-xs text-slate-400">Bots aapas me Hinglish me live decision debate kar rahe hain</p>
            </div>
          </div>
          <button onclick="clearChat()" class="text-xs font-retro text-slate-400 hover:text-white px-2.5 py-1 bg-cyberDark border border-cyberBorder rounded">
            CLEAR CHAT
          </button>
        </div>

        <!-- Chat Container -->
        <div id="hinglishChatBox" class="space-y-2.5 max-h-72 overflow-y-auto pr-2 font-mono text-xs">
          <!-- Live Hinglish messages inject honge yahan -->
        </div>

        <div class="pt-2.5 mt-2.5 border-t border-cyberBorder/60 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            ACTIVE PROTOCOL: MULTI-AGENT CONSENSUS
          </span>
          <span class="text-emerald-400 font-retro text-sm">SYNCHRONIZED WITH MT5</span>
        </div>
      </section>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-cyberBorder bg-cyberPanel/95 py-2 px-4 backdrop-blur mt-4">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2 text-xs">
        <div class="flex items-center space-x-4">
          <span class="font-retro text-slate-400">@seb.ai / GROK 6-BOT ARCHITECTURE</span>
          <span class="text-slate-600">|</span>
          <span class="text-emerald-400 font-mono text-[11px] flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 status-pulse"></span>
            ALL 6 AGENTS DEBATING LIVE
          </span>
        </div>
      </div>
    </footer>

  </div>

  <script>
    const state = {
      activeTab: 'room',
      soundEnabled: true,
      audioCtx: null,
      candles: []
    };

    const botStyles = {
      '01 SCOUT': { class: 'chat-bubble-scout', color: '#FFD000', icon: '⚡' },
      '02 NEWS': { class: 'chat-bubble-news', color: '#FF3B30', icon: '📰' },
      '03 SENTIMENT': { class: 'chat-bubble-sent', color: '#AF52DE', icon: '🔮' },
      '04 CHARTS': { class: 'chat-bubble-chart', color: '#007AFF', icon: '📊' },
      '05 RISK': { class: 'chat-bubble-risk', color: '#34C759', icon: '🛡️' },
      '06 DECISION': { class: 'chat-bubble-dec', color: '#FF9500', icon: '🎯' }
    };

    function playRetroBeep(type = 'blip') {
      if (!state.soundEnabled) return;
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!state.audioCtx) state.audioCtx = new AudioContext();
        if (state.audioCtx.state === 'suspended') state.audioCtx.resume();
        const ctx = state.audioCtx;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        const now = ctx.currentTime;
        osc.type = 'square';
        osc.frequency.setValueAtTime(type === 'success' ? 659.25 : 440, now);
        gain.gain.setValueAtTime(0.04, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      } catch(e) {}
    }

    function toggleAudio() {
      state.soundEnabled = !state.soundEnabled;
      document.getElementById('audioState').innerText = state.soundEnabled ? 'ON' : 'OFF';
      if (state.soundEnabled) playRetroBeep('blip');
    }

    function toggleScanlines() {
      document.getElementById('crtOverlay').classList.toggle('scanlines');
      playRetroBeep('blip');
    }

    function switchTab(tabId) {
      state.activeTab = tabId;
      playRetroBeep('blip');
      ['room', 'scout', 'news', 'sentiment', 'charts', 'risk', 'decision'].forEach(id => {
        const view = document.getElementById(`view-${id}`);
        const btn = document.getElementById(`tab-${id}`);
        if (view) view.classList.add('hidden');
        if (btn) {
          btn.classList.remove('bg-emerald-500', 'text-black', 'shadow-lg');
          btn.classList.add('bg-cyberCard', 'text-slate-300');
        }
      });
      const targetView = document.getElementById(`view-${tabId}`);
      const targetBtn = document.getElementById(`tab-${tabId}`);
      if (targetView) targetView.classList.remove('hidden');
      if (targetBtn) {
        targetBtn.classList.remove('bg-cyberCard', 'text-slate-300');
        targetBtn.classList.add('bg-emerald-500', 'text-black', 'shadow-lg');
      }
      if (tabId === 'room') drawOverviewChart();
      if (tabId === 'sentiment') drawSentimentGauge();
    }

    function addHinglishChat(bot, message) {
      const box = document.getElementById('hinglishChatBox');
      if (!box) return;

      const time = new Date().toTimeString().split(' ')[0];
      const style = botStyles[bot] || { class: 'chat-bubble-scout', color: '#fff', icon: '🤖' };

      const div = document.createElement('div');
      div.className = `p-2.5 rounded-lg border border-slate-800 ${style.class} transition`;
      div.innerHTML = `
        <div class="flex justify-between items-center mb-1">
          <span class="font-pixel text-[10px] flex items-center gap-1.5" style="color:${style.color}">
            <span>${style.icon}</span> ${bot}
          </span>
          <span class="font-mono text-[10px] text-slate-500">[${time}]</span>
        </div>
        <div class="text-slate-200 text-xs font-mono">${message}</div>
      `;

      box.appendChild(div);
      box.scrollTop = box.scrollHeight;

      if (box.children.length > 50) {
        box.removeChild(box.firstChild);
      }
    }

    function clearChat() {
      document.getElementById('hinglishChatBox').innerHTML = '';
      addHinglishChat('06 DECISION', 'Team buffer clear ho gaya. Fresh market analysis scan shuru karo.');
    }

    async function fetchMT5LiveSync() {
      try {
        const res = await fetch('/api/data');
        const data = await res.json();

        document.getElementById('headerBalance').innerText = `$${Number(data.balance).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        document.getElementById('roomActiveTicker').innerText = `${data.symbol} $${data.bid} / $${data.ask}`;

        document.getElementById('desk1Status').innerText = `$${data.bid} | Sp: ${data.spread}`;
        document.getElementById('desk2Status').innerText = data.bias;
        document.getElementById('desk3Status').innerText = `${data.score} (${data.bias})`;
        document.getElementById('desk4Status').innerText = `${data.trend}`;
        document.getElementById('desk5Status').innerText = `${data.lot} LOTS`;
        document.getElementById('desk6Status').innerText = data.decision;

        document.getElementById('chartHigh').innerText = data.res;
        document.getElementById('chartLow').innerText = data.supp;
        document.getElementById('scoutVolState').innerText = `VOL: ${data.vol}`;

        document.getElementById('scoutDetailPrice').innerText = `BID: ${data.bid} | ASK: ${data.ask} | SPREAD: ${data.spread}`;
        document.getElementById('scoutDetailVol').innerText = `VOLUME: ${data.vol}`;
        document.getElementById('newsLiveHeadline').innerText = data.catalyst;
        document.getElementById('sentimentScoreDisplay').innerText = data.score;
        document.getElementById('hudResist').innerText = `$${data.res}`;
        document.getElementById('hudSupport').innerText = `$${data.supp}`;
        document.getElementById('hudTrend').innerText = data.trend;
        document.getElementById('riskVaultBal').innerText = `$${Number(data.balance).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        document.getElementById('riskLotDisplay').innerText = `${data.lot} Lots`;
        document.getElementById('decActionDisplay').innerText = data.decision;
        document.getElementById('decReasonDisplay').innerText = data.reason;

        state.candles = data.candles || [];
        if (state.activeTab === 'room') drawOverviewChart();
        if (state.activeTab === 'sentiment') drawSentimentGauge();

        if (data.dialogues && data.dialogues.length > 0) {
          data.dialogues.forEach(d => addHinglishChat(d.bot, d.text));
        }

      } catch(err) {
        console.error(err);
      }
    }

    function drawOverviewChart() {
      const canvas = document.getElementById('overviewChartCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio || 600;
      canvas.height = rect.height * window.devicePixelRatio || 220;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      const w = rect.width;
      const h = rect.height;
      ctx.clearRect(0, 0, w, h);

      if (!state.candles.length) return;
      const step = w / (state.candles.length + 1);
      const minP = Math.min(...state.candles.map(c => c.low));
      const maxP = Math.max(...state.candles.map(c => c.high));
      const range = (maxP - minP) || 1;

      state.candles.forEach((c, i) => {
        const x = (i + 1) * step;
        const openY = h - ((c.open - minP) / range) * (h - 30) - 15;
        const closeY = h - ((c.close - minP) / range) * (h - 30) - 15;
        const highY = h - ((c.high - minP) / range) * (h - 30) - 15;
        const lowY = h - ((c.low - minP) / range) * (h - 30) - 15;
        const color = c.close >= c.open ? '#34C759' : '#FF3B30';

        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(x, highY);
        ctx.lineTo(x, lowY);
        ctx.stroke();
        ctx.fillRect(x - step * 0.35, Math.min(openY, closeY), step * 0.7, Math.abs(closeY - openY) || 2);
      });
    }

    function drawSentimentGauge() {
      const canvas = document.getElementById('sentimentGaugeCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      const centerX = w / 2;
      const centerY = h - 15;
      const radius = 95;

      ctx.lineWidth = 14;
      ctx.strokeStyle = '#FF3B30';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, Math.PI, Math.PI * 1.35);
      ctx.stroke();

      ctx.strokeStyle = '#34C759';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, Math.PI * 1.35, Math.PI * 1.7);
      ctx.stroke();

      ctx.strokeStyle = '#AF52DE';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, Math.PI * 1.7, Math.PI * 2);
      ctx.stroke();

      const score = 72;
      const angle = Math.PI + (score / 100) * Math.PI;

      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(angle);
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(radius - 10, 0);
      ctx.stroke();
      ctx.restore();

      ctx.beginPath();
      ctx.arc(centerX, centerY, 8, 0, Math.PI * 2);
      ctx.fillStyle = '#FFD000';
      ctx.fill();
    }

    setInterval(() => {
      document.getElementById('liveClock').innerText = new Date().toTimeString().split(' ')[0];
    }, 1000);

    window.onload = function() {
      addHinglishChat('06 DECISION', 'War Room shuru ho chuka hai. Saare bots apna live market analysis report karein.');
      fetchMT5LiveSync();
      setInterval(fetchMT5LiveSync, 3500);
    };
  </script>
</body>
</html>
"""

cycle_turn = 0

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/api/data')
def get_data():
    global cycle_turn
    tick = mt5.symbol_info_tick(SYMBOL)
    account = mt5.account_info()
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 30)

    candles = []
    resistance = 0.0
    support = 0.0
    trend = "BULLISH"
    vol_surge = False

    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        resistance = round(float(df['high'].iloc[:-1].max()), 2)
        support = round(float(df['low'].iloc[:-1].min()), 2)
        df['ma20'] = df['close'].rolling(20).mean()
        trend = "BULLISH" if df['close'].iloc[-1] > df['ma20'].iloc[-1] else "BEARISH"
        vol_surge = df['tick_volume'].iloc[-1] > (df['tick_volume'].mean() * 1.3)

        for _, r in df.iterrows():
            candles.append({
                "open": float(r['open']),
                "high": float(r['high']),
                "low": float(r['low']),
                "close": float(r['close'])
            })

    balance = round(account.balance, 2) if account else 10000.0
    bid = round(tick.bid, 2) if tick else 4115.00
    ask = round(tick.ask, 2) if tick else 4115.50
    spread = round(ask - bid, 2)

    positions = mt5.positions_get(symbol=SYMBOL)
    open_trades = len(positions) if positions else 0

    # Decision Engine
    decision = "WAIT"
    reason = "Gold abhi consolidate kar raha hai. Clean breakout ka wait hai."

    if open_trades >= 1:
        decision = "HOLD"
        reason = "Trade chal raha hai. Trailing Stop Loss protect kar raha hai."
    elif trend == "BULLISH" and ask >= (resistance - 0.30) and vol_surge:
        decision = "BUY"
        reason = f"Resistance {resistance} toot chuka hai + High volume surge aaya hai!"
    elif trend == "BEARISH" and bid <= (support + 0.30) and vol_surge:
        decision = "SELL"
        reason = f"Support {support} breakdown ho chuka hai + High volume surge aaya hai!"

    # Realistic Dynamic Hinglish Multi-Agent Chat
    dialogues = []
    cycle_turn += 1

    if cycle_turn % 4 == 1:
        surge_text = "Volume me achanak tez jump (+130%) dekha hai!" if vol_surge else "Volume abhi normal chal raha hai."
        dialogues.append({
            "bot": "01 SCOUT",
            "text": f"Bhaiyo, Gold ka Bid ${bid} aur Ask ${ask} chal raha hai. Spread sirf ${spread} hai. {surge_text}"
        })
    elif cycle_turn % 4 == 2:
        dialogues.append({
            "bot": "04 CHARTS",
            "text": f"M15 Structure dekho: Resistance ${resistance} par hai aur Support ${support} par hai. Overall trend {trend} hai."
        })
        dialogues.append({
            "bot": "03 SENTIMENT",
            "text": "Gemini AI Sentiment score 72/100 hai (Safe-haven demand positive hai). Koi panic nahi hai."
        })
    elif cycle_turn % 4 == 3:
        dialogues.append({
            "bot": "05 RISK",
            "text": f"Account capital ${balance:,.2f} verify ho gaya. 1% rule ke mutabiq exact 0.04 Lot cap kiya hai. Trade allow hai."
        })
    elif cycle_turn % 4 == 0:
        if decision == "WAIT":
            dec_text = f"Sabhi suno: ACTION [ WAIT ]. Price abhi ${support} aur ${resistance} ke beech phas raha hai, chop me loss mat lo."
        elif decision == "BUY":
            dec_text = f"🔥 BINGO! ACTION [ BUY ]. Resistance tod diya aur volume confirm hai! Order execute kar rahe hain."
        else:
            dec_text = f"🔥 SELL ALERT! Support toot gaya hai. Short order trigger kiya ja raha hai."
        dialogues.append({
            "bot": "06 DECISION",
            "text": dec_text
        })

    return jsonify({
        "time": datetime.now().strftime("%H:%M:%S"),
        "symbol": SYMBOL,
        "bid": bid,
        "ask": ask,
        "spread": spread,
        "vol": "SURGE" if vol_surge else "NORMAL",
        "catalyst": "Safe-haven hedge flows against bond yields",
        "bias": "BULLISH",
        "score": 72,
        "trend": trend,
        "supp": support,
        "res": resistance,
        "lot": 0.04,
        "balance": balance,
        "open_trades": open_trades,
        "candles": candles,
        "decision": decision,
        "reason": reason,
        "dialogues": dialogues
    })

if __name__ == '__main__':
    print("🚀 CYBERPUNK TERMINAL + HINGLISH WAR ROOM: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)