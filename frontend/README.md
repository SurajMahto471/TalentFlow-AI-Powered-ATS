# TalentFlow ATS — React Dashboard

Enterprise-grade AI-Powered Applicant Tracking System frontend built with React, Tailwind CSS, Shadcn UI patterns, Framer Motion, and Recharts.

## Tech Stack

- **React 18** + TypeScript + Vite
- **Tailwind CSS** — utility-first styling with dark mode
- **Shadcn UI** — Radix-based component patterns
- **Framer Motion** — page transitions and micro-animations
- **Recharts** — analytics charts and funnel visualization
- **React Router** — client-side navigation

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

## Project Structure

```
src/
├── components/
│   ├── ui/           # Shadcn-style primitives (Button, Card, Badge…)
│   ├── layout/       # Sidebar, TopNav, MainLayout
│   ├── dashboard/    # StatCard, CandidateTable, AnalyticsCharts
│   └── ats/          # ScoreGauge
├── pages/            # Route-level pages
├── contexts/         # ThemeProvider (dark mode)
├── data/             # Mock candidate & analytics data
├── types/            # TypeScript interfaces
└── lib/              # Utility functions
```

## Pages

| Route | Page |
|-------|------|
| `/` | Dashboard with stats, charts, rankings |
| `/candidates` | Full candidate table with search/filter/sort |
| `/candidates/:id` | Candidate detail with ATS gauge & resume |
| `/jobs` | Job description management |
| `/scoring` | ATS scoring breakdown |
| `/skill-gap` | Skill gap analysis with recommendations |
| `/interview` | AI interview question generator |
| `/analytics` | Hiring analytics |
| `/upload` | Drag-and-drop resume upload |
| `/settings` | Profile & preferences |

## Connect to Python Backend

The Vite dev server proxies `/api/*` to `http://localhost:8000` (FastAPI).

Start the backend:

```bash
python -m uvicorn api:app --reload --port 8000
```

## Build for Production

```bash
npm run build
npm run preview
```
