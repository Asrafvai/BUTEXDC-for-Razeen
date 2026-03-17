# BUTEX Debating Club Platform - PRD

## Original Problem Statement
Build a modern, minimal, fully responsive training and management platform for the BUTEX Debating Club. Non-technical admins must be able to manage all dynamic content from a frontend admin dashboard.

## Tech Stack
- **Backend:** FastAPI + MongoDB
- **Frontend:** React + Tailwind CSS + Shadcn UI + Swiper.js
- **Auth:** Custom JWT
- **Database:** MongoDB via motor (async pymongo)

## What's Been Implemented
- Full auth system (signup, login, admin/student roles, pending/approved)
- Public pages: Home, Leadership, Announcements, Courses, Success Events, Alumni, Events and Sessions, Be a Member, Coach
- Admin dashboard with management for all content types
- Dark/Light theme toggle
- Success Stories carousel + Events and Sessions carousel on homepage
- Homepage hero with large club logo
- Social media section (Facebook Page + Group links)
- Alumni batch filter (grouped by batch, dropdown)
- Public course/module viewing (modules locked, redirect to signup)
- Student dashboard with Events (Watch/Get Note buttons) + Announcements sections
- **Flagship Events** — full feature: admin CRUD with event announcements, big photo cards on homepage, dedicated event pages with embedded Google Form pre-registration (Mar 17, 2026)

## Credentials
- Admin: admin@butexdc.edu.bd / admin123

## DB Collections
users, courses, modules, announcements, leadership, success_events, alumni, events, membership, flagship_events, flagship_announcements

## Key API Endpoints
- `/api/auth/*` — login, signup, me
- `/api/admin/*` — all admin CRUD
- `/api/flagship-events`, `/api/flagship-events/:id` — public flagship
- `/api/admin/flagship-events/*` — admin flagship CRUD
- `/api/admin/flagship-events/:id/announcements` — event announcements
- `/api/courses`, `/api/courses/:id/modules` — public courses

## Pending Issues
1. (P1) Images not displaying on production (CSP/URL issues)
2. (P1) Deployment errors: PUT /api/admin/leadership/{id} 404
3. (P2) Production readiness: JWT secret key, N+1 analytics query

## Upcoming Tasks
- (P1) Student progress tracking (mark modules complete, progress bars)
- (P1) Drag-and-drop reordering for leadership & modules
- (P2) Complete admin user management (last_login, archive)

## Backlog
- (P3) Backend refactoring: split server.py into routes/models/services
