# CyberLearn - Cybersecurity Learning App Blueprint (V1)

---

## 1. Product Overview

### 1.1 One-Sentence Elevator Pitch

**CyberLearn is a bite-sized, interactive learning app that teaches practical cybersecurity skills through scenario-based challenges, code exercises, and real-world simulations—designed for busy professionals who want hands-on security knowledge, not certification cramming.**

---

### 1.2 Primary Goals (V1)

| # | Goal | Success Metric |
|---|------|----------------|
| 1 | **Validate engagement model** | 40%+ of signups complete at least 10 lessons within first 14 days |
| 2 | **Prove learning retention** | Users score 70%+ on end-of-module assessments |
| 3 | **Build habit loop** | 25%+ of active users maintain a 7-day streak in month 1 |
| 4 | **Content-market fit** | NPS > 40 from beta users; qualitative feedback confirms "practical, not boring" |
| 5 | **Technical foundation** | Ship stable platform supporting 1,000 concurrent users with <200ms API p95 latency |

---

### 1.3 Target Personas

#### Persona 1: Alex – Helpdesk Tech Transitioning to Security

| Attribute | Details |
|-----------|---------|
| **Role** | IT Helpdesk Analyst (2 years), wants to become SOC Analyst |
| **Age** | 26 |
| **Motivations** | Wants a career upgrade with better pay; fascinated by security incidents they hear about at work |
| **Pain Points** | Traditional courses are too long and theoretical; can't afford bootcamps; doesn't know where to start |
| **Success in App** | Completes "Blue Team Basics" track, confidently applies for junior SOC roles, passes Security+ within 6 months |

#### Persona 2: Maya – Developer Who Wants to Code Securely

| Attribute | Details |
|-----------|---------|
| **Role** | Full-stack developer at a startup (3 years experience) |
| **Age** | 29 |
| **Motivations** | Embarrassed after their code caused a vulnerability; wants to understand OWASP Top 10 deeply |
| **Pain Points** | Security docs are dense; doesn't have time for week-long courses; wants practical "show me the code" examples |
| **Success in App** | Completes "Secure Coding" track, catches injection vulnerabilities in PR reviews, becomes team's go-to for security questions |

#### Persona 3: Jordan – Career Changer / Tech-Curious Beginner

| Attribute | Details |
|-----------|---------|
| **Role** | Marketing coordinator considering tech career pivot |
| **Age** | 32 |
| **Motivations** | Heard cybersecurity is "in demand"; wants to test if it's right for them before committing to expensive training |
| **Pain Points** | Overwhelmed by jargon; doesn't know difference between "ethical hacking" and "compliance"; needs beginner-friendly on-ramp |
| **Success in App** | Completes "Cyber Foundations" track, decides to pursue security career, enrolls in structured program with confidence |

---

## 2. Learning Model & Content Structure

### 2.1 Content Hierarchy

```
Platform
└── Track (e.g., "Blue Team Basics")
    └── Module (e.g., "Understanding Threats")
        └── Lesson (e.g., "What is Malware?")
            └── Step (micro-interaction: read / quiz / code / scenario)
```

#### Definitions

| Unit | Description | Typical Size |
|------|-------------|--------------|
| **Track** | A complete learning path focused on a domain or career goal | 8-15 modules, ~20-40 hours total |
| **Module** | A thematic grouping of related concepts | 5-10 lessons, ~2-4 hours |
| **Lesson** | A single focused topic that can be completed in one sitting | 5-12 steps, ~5-15 minutes |
| **Step** | The atomic unit of interaction—one screen, one action | 30 seconds - 2 minutes |

#### V1 Tracks

1. **Cyber Foundations** – For complete beginners (CIA triad, threat landscape, basic terminology)
2. **Blue Team Basics** – Defensive security (log analysis, incident detection, basic forensics)
3. **Secure Coding Essentials** – For developers (OWASP Top 10, input validation, auth best practices)

---

### 2.2 Lesson Types (Step Types)

| Type | Description | Example | Interactivity |
|------|-------------|---------|---------------|
| **Concept Explainer** | Short text + optional diagram explaining a concept | "What is SQL Injection?" with visual showing data flow | Read + "Got it" button |
| **Multiple Choice Quiz** | Single or multi-select question testing comprehension | "Which of these is NOT a type of malware?" | Select answer(s), immediate feedback |
| **Code Challenge** | Write or complete code/commands in embedded editor | "Write a grep command to find failed SSH logins in this log" | Code input, automated validation |
| **Scenario Decision** | Present a realistic situation, user chooses action | "You receive this email. What do you do?" (with screenshot) | Choice selection, branching feedback |
| **Fix the Config** | Given a misconfigured file, user must correct it | "This nginx config has 3 security issues. Fix them." | Diff-based editor, validation |
| **Spot the Vulnerability** | Code or config shown, user identifies the flaw | "Which line contains the XSS vulnerability?" | Line selection or highlight |
| **Fill in the Blank** | Complete a command, config line, or statement | "To check open ports, run: `nmap ___ target`" | Text input with fuzzy matching |
| **Drag and Drop** | Order steps or match concepts | "Put these incident response steps in order" | Drag UI, order validation |

---

### 2.3 Gamification Layer

#### Core Mechanics

| Mechanic | Implementation |
|----------|----------------|
| **XP (Experience Points)** | Earned per step completed. Base: 10 XP/step. Bonus: +5 XP for correct on first try, +10 XP for streak bonus |
| **Levels** | XP thresholds: Level 1 = 0 XP, Level 2 = 100 XP, Level 3 = 300 XP, etc. (exponential curve, max Level 50 in V1) |
| **Streaks** | Daily streak counted if user completes ≥1 lesson per calendar day (user's timezone). Streak freeze purchasable with XP later |
| **Hearts/Lives** | NOT implementing. Research shows it frustrates learners. Unlimited attempts with XP bonus for first-try success instead |

#### Badges (V1 Set)

| Badge | Criteria |
|-------|----------|
| **First Step** | Complete your first lesson |
| **Week Warrior** | 7-day streak |
| **Module Master: [Name]** | Complete any module with 80%+ quiz accuracy |
| **Phishing Spotter** | Complete all phishing-related lessons |
| **Code Defender** | Complete 10 code challenges |
| **Night Owl** | Complete a lesson between 12am-5am |
| **Speed Demon** | Complete a lesson in under 3 minutes with 100% accuracy |

#### Future: Daily/Weekly Challenges (V1.5)

- **Daily Challenge**: One random question from completed content, +50 XP bonus
- **Weekly Challenge**: Mini-assessment covering week's learning, badge + XP reward

---

## 3. Feature Set for V1

### 3.1 Core Features (Must-Have for V1)

#### Authentication & Onboarding
- [ ] Email/password registration with email verification
- [ ] OAuth sign-in (Google, Microsoft)—critical for enterprise later
- [ ] Onboarding flow: skill assessment quiz (5-7 questions) → recommended starting track
- [ ] Profile setup: display name, avatar selection (preset options), timezone

#### Learning Experience
- [ ] Track browser: view all tracks, see progress percentage
- [ ] Lesson player: renders all step types (concept, quiz, code, scenario, etc.)
- [ ] Progress persistence: every step completion saved, resume from exact position
- [ ] Immediate feedback on answers (correct/incorrect + explanation)
- [ ] Code execution environment: sandboxed runner for bash/Python snippets (simple validation, not full sandbox)
- [ ] Module assessments: end-of-module quiz (graded, affects badge eligibility)

#### Dashboard & Progress
- [ ] Home dashboard: "Continue Learning" card, current streak, daily XP goal progress
- [ ] Profile page: level, total XP, badges earned, tracks completed
- [ ] Progress indicators: per-track, per-module, per-lesson completion status
- [ ] Streak counter with visual calendar (GitHub-contribution-style)

#### Content & Data
- [ ] Static content system: lessons stored as structured JSON/MDX, versioned
- [ ] At least 3 tracks with 3+ modules each, totaling ~50 lessons for launch
- [ ] Content supports: markdown text, images, code blocks with syntax highlighting

#### Infrastructure
- [ ] Responsive web design (desktop + mobile web)
- [ ] Basic analytics: track completion rates, drop-off points, quiz accuracy
- [ ] Error tracking and logging

---

### 3.2 Nice-to-Have (V1.5+)

| Feature | Priority | Notes |
|---------|----------|-------|
| Friend system & leaderboards | High | Social accountability drives retention |
| Admin content editor (CMS) | High | Currently content via JSON files; need GUI for content team |
| Push notifications (web) | Medium | Streak reminders, new content alerts |
| Certification path mapping | Medium | Map lessons to Security+/CISSP domains |
| Interactive terminal sandbox | Medium | Real bash/Linux environment for advanced labs |
| Offline mode (PWA) | Low | Download lessons for offline completion |
| Discussion/comments per lesson | Low | Community Q&A, requires moderation |
| Team/organization accounts | Future | For enterprise sales |
| SCORM/LTI export | Future | LMS integration for enterprises |

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 CLIENTS                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │  Web App     │  │  Mobile Web  │  │  Future:     │                       │
│  │  (Next.js)   │  │  (Responsive)│  │  Native Apps │                       │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘                       │
└─────────┼─────────────────┼─────────────────────────────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CDN (CloudFlare/Vercel Edge)                    │
│                     Static assets, caching, DDoS protection                  │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY / LOAD BALANCER                     │
│                          (Rate limiting, request routing)                    │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND SERVICES (NestJS)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Auth      │ │   User      │ │  Content    │ │  Progress   │           │
│  │   Module    │ │   Module    │ │  Module     │ │  Module     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │ Gamification│ │  Analytics  │ │   Admin     │                           │
│  │   Module    │ │   Module    │ │   Module    │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
          │                   │                    │
          ▼                   ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   PostgreSQL     │ │      Redis       │ │   Object Storage │
│   (Primary DB)   │ │   (Cache/Queue)  │ │   (S3/R2/Minio)  │
│                  │ │                  │ │                  │
│ - Users          │ │ - Session store  │ │ - Images         │
│ - Progress       │ │ - Rate limiting  │ │ - Lesson assets  │
│ - Gamification   │ │ - Leaderboards   │ │ - User uploads   │
│ - Analytics      │ │ - Job queues     │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │
          ▼
┌──────────────────┐
│  Code Execution  │
│  Sandbox (Piston │
│  or Judge0)      │
└──────────────────┘
```

---

### 4.2 Tech Stack Choices & Justification

#### Frontend: Next.js 14 (App Router)

| Reason | Details |
|--------|---------|
| **SSR for marketing pages** | Landing page, pricing, blog need SEO; Next.js handles SSR/SSG natively |
| **React ecosystem** | Largest talent pool, best component libraries (Radix, shadcn/ui) |
| **API routes for BFF** | Can proxy/aggregate backend calls, reducing client complexity |
| **Vercel deployment** | Zero-config deployments, edge functions, great DX |
| **Future mobile path** | React knowledge transfers to React Native |

**Alternative considered**: SvelteKit—faster runtime, but smaller ecosystem and harder to hire for.

#### Backend: NestJS (Node.js/TypeScript)

| Reason | Details |
|--------|---------|
| **TypeScript end-to-end** | Same language as frontend; shared types, faster development |
| **Modular architecture** | Built-in module system maps perfectly to our service domains |
| **Enterprise patterns** | Dependency injection, guards, interceptors—scales well |
| **Strong ORM support** | First-class Prisma/TypeORM integration |
| **Auth ecosystem** | Passport.js integration for OAuth, JWT strategies |

**Alternative considered**: FastAPI (Python)—excellent for ML-heavy apps, but we don't need ML in V1; TypeScript consistency wins.

#### Database: PostgreSQL 15

| Reason | Details |
|--------|---------|
| **Relational data model** | Users, progress, content relationships are inherently relational |
| **JSON support** | `jsonb` columns for flexible lesson step data |
| **Proven scale** | Handles millions of users with proper indexing |
| **Tooling** | Prisma migrations, pg_dump backups, read replicas when needed |

#### Cache & Sessions: Redis 7

| Reason | Details |
|--------|---------|
| **Session storage** | Faster than DB for session lookups |
| **Rate limiting** | Sliding window counters for API protection |
| **Leaderboards** | Sorted sets for real-time XP rankings |
| **Job queues** | BullMQ for background tasks (email, analytics aggregation) |

#### Code Execution: Piston (Self-Hosted) or Judge0

| Reason | Details |
|--------|---------|
| **Sandboxed execution** | Run user code safely (bash, Python) in isolated containers |
| **Multi-language** | Supports 50+ languages if we expand |
| **Timeout controls** | Kill runaway processes automatically |

**V1 approach**: Start with simple regex/output matching for code challenges; add Piston in V1.5 for true execution.

#### Object Storage: Cloudflare R2 or AWS S3

| Reason | Details |
|--------|---------|
| **Static assets** | Lesson images, diagrams, downloadable resources |
| **Cost effective** | R2 has zero egress fees |
| **CDN integration** | Serve via edge for fast global delivery |

---

### 4.3 Backend Modules (NestJS Structure)

```
src/
├── auth/
│   ├── auth.module.ts
│   ├── auth.controller.ts        # Login, register, OAuth callbacks
│   ├── auth.service.ts           # Token generation, validation
│   ├── strategies/               # Passport strategies (local, Google, Microsoft)
│   ├── guards/                   # JwtAuthGuard, RolesGuard
│   └── dto/                      # LoginDto, RegisterDto
│
├── users/
│   ├── users.module.ts
│   ├── users.controller.ts       # Profile CRUD, settings
│   ├── users.service.ts          # User business logic
│   └── entities/user.entity.ts
│
├── content/
│   ├── content.module.ts
│   ├── content.controller.ts     # Get tracks, modules, lessons
│   ├── content.service.ts        # Content retrieval, caching
│   ├── entities/                 # Track, Module, Lesson, Step entities
│   └── loaders/                  # JSON/MDX content loaders
│
├── progress/
│   ├── progress.module.ts
│   ├── progress.controller.ts    # Get/update user progress
│   ├── progress.service.ts       # Completion logic, resume points
│   └── entities/                 # UserProgress, LessonCompletion
│
├── gamification/
│   ├── gamification.module.ts
│   ├── gamification.controller.ts # XP, levels, badges, streaks
│   ├── gamification.service.ts    # XP calculations, badge awards
│   ├── entities/                  # UserXP, Badge, UserBadge, Streak
│   └── events/                    # Event handlers for XP triggers
│
├── analytics/
│   ├── analytics.module.ts
│   ├── analytics.service.ts      # Track events, aggregate metrics
│   └── entities/                 # AnalyticsEvent
│
├── admin/
│   ├── admin.module.ts
│   ├── admin.controller.ts       # Content management (V1.5), user management
│   └── admin.guard.ts            # Admin role verification
│
├── execution/
│   ├── execution.module.ts
│   ├── execution.service.ts      # Code validation, sandbox integration
│   └── validators/               # Language-specific validators
│
└── common/
    ├── interceptors/             # Logging, transform
    ├── filters/                  # Exception handling
    ├── decorators/               # Custom decorators
    └── utils/                    # Shared utilities
```

---

## 5. Data Model (First Pass)

### Core Entities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   USER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ email           VARCHAR(255) UNIQUE NOT NULL                                │
│ password_hash   VARCHAR(255) NULL (null if OAuth-only)                      │
│ display_name    VARCHAR(100) NOT NULL                                       │
│ avatar_url      VARCHAR(500) NULL                                           │
│ timezone        VARCHAR(50) DEFAULT 'UTC'                                   │
│ email_verified  BOOLEAN DEFAULT FALSE                                       │
│ oauth_provider  VARCHAR(50) NULL (google, microsoft)                        │
│ oauth_id        VARCHAR(255) NULL                                           │
│ role            ENUM('user', 'admin') DEFAULT 'user'                        │
│ onboarding_done BOOLEAN DEFAULT FALSE                                       │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
│ updated_at      TIMESTAMP DEFAULT NOW()                                     │
│ last_login_at   TIMESTAMP NULL                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                   TRACK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ slug            VARCHAR(100) UNIQUE NOT NULL                                │
│ title           VARCHAR(200) NOT NULL                                       │
│ description     TEXT NOT NULL                                               │
│ difficulty      ENUM('beginner', 'intermediate', 'advanced')                │
│ estimated_hours INTEGER NOT NULL                                            │
│ icon_url        VARCHAR(500) NULL                                           │
│ color           VARCHAR(7) NULL (hex color for UI)                          │
│ is_published    BOOLEAN DEFAULT FALSE                                       │
│ order_index     INTEGER NOT NULL                                            │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
│ updated_at      TIMESTAMP DEFAULT NOW()                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                  MODULE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ track_id        UUID REFERENCES track(id) ON DELETE CASCADE                 │
│ slug            VARCHAR(100) NOT NULL                                       │
│ title           VARCHAR(200) NOT NULL                                       │
│ description     TEXT NOT NULL                                               │
│ order_index     INTEGER NOT NULL                                            │
│ is_published    BOOLEAN DEFAULT FALSE                                       │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
│ updated_at      TIMESTAMP DEFAULT NOW()                                     │
│ UNIQUE(track_id, slug)                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                  LESSON                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ module_id       UUID REFERENCES module(id) ON DELETE CASCADE                │
│ slug            VARCHAR(100) NOT NULL                                       │
│ title           VARCHAR(200) NOT NULL                                       │
│ description     TEXT NULL                                                   │
│ estimated_mins  INTEGER NOT NULL                                            │
│ xp_reward       INTEGER DEFAULT 50                                          │
│ order_index     INTEGER NOT NULL                                            │
│ is_published    BOOLEAN DEFAULT FALSE                                       │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
│ updated_at      TIMESTAMP DEFAULT NOW()                                     │
│ UNIQUE(module_id, slug)                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                               LESSON_STEP                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ lesson_id       UUID REFERENCES lesson(id) ON DELETE CASCADE                │
│ order_index     INTEGER NOT NULL                                            │
│ step_type       ENUM('concept', 'quiz_single', 'quiz_multi', 'code',       │
│                      'scenario', 'fix_config', 'spot_vuln', 'fill_blank',  │
│                      'drag_drop')                                           │
│ content         JSONB NOT NULL  -- structured content for the step          │
│ xp_value        INTEGER DEFAULT 10                                          │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
│ updated_at      TIMESTAMP DEFAULT NOW()                                     │
└─────────────────────────────────────────────────────────────────────────────┘

-- Example content JSONB for different step types:

-- concept:
-- {
--   "title": "What is SQL Injection?",
--   "body": "SQL injection is a code injection technique...",
--   "image_url": "/assets/sql-injection-diagram.png",
--   "highlights": ["user input", "database query"]
-- }

-- quiz_single:
-- {
--   "question": "Which protocol is used for secure web traffic?",
--   "options": [
--     {"id": "a", "text": "HTTP", "is_correct": false},
--     {"id": "b", "text": "HTTPS", "is_correct": true},
--     {"id": "c", "text": "FTP", "is_correct": false}
--   ],
--   "explanation": "HTTPS uses TLS encryption to secure traffic."
-- }

-- code:
-- {
--   "prompt": "Write a command to find failed SSH login attempts",
--   "language": "bash",
--   "starter_code": "grep ___ /var/log/auth.log",
--   "expected_patterns": ["Failed password", "auth.log"],
--   "validation_type": "regex",
--   "hints": ["Look for 'Failed' in the auth log"]
-- }

┌─────────────────────────────────────────────────────────────────────────────┐
│                             USER_PROGRESS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ user_id         UUID REFERENCES user(id) ON DELETE CASCADE                  │
│ lesson_id       UUID REFERENCES lesson(id) ON DELETE CASCADE                │
│ current_step    INTEGER DEFAULT 0  -- index of current step                 │
│ status          ENUM('not_started', 'in_progress', 'completed')             │
│ score           INTEGER NULL  -- percentage for graded lessons              │
│ started_at      TIMESTAMP NULL                                              │
│ completed_at    TIMESTAMP NULL                                              │
│ UNIQUE(user_id, lesson_id)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            STEP_COMPLETION                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ user_id         UUID REFERENCES user(id) ON DELETE CASCADE                  │
│ step_id         UUID REFERENCES lesson_step(id) ON DELETE CASCADE           │
│ is_correct      BOOLEAN NULL  -- null for non-graded steps                  │
│ attempts        INTEGER DEFAULT 1                                           │
│ xp_earned       INTEGER NOT NULL                                            │
│ user_answer     JSONB NULL  -- store what they submitted                    │
│ completed_at    TIMESTAMP DEFAULT NOW()                                     │
│ UNIQUE(user_id, step_id)                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           GAMIFICATION_PROFILE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ user_id         UUID REFERENCES user(id) ON DELETE CASCADE UNIQUE           │
│ total_xp        INTEGER DEFAULT 0                                           │
│ level           INTEGER DEFAULT 1                                           │
│ current_streak  INTEGER DEFAULT 0                                           │
│ longest_streak  INTEGER DEFAULT 0                                           │
│ last_activity   DATE NULL  -- for streak calculation                        │
│ updated_at      TIMESTAMP DEFAULT NOW()                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                 BADGE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ slug            VARCHAR(100) UNIQUE NOT NULL                                │
│ name            VARCHAR(200) NOT NULL                                       │
│ description     TEXT NOT NULL                                               │
│ icon_url        VARCHAR(500) NOT NULL                                       │
│ criteria_type   VARCHAR(50) NOT NULL  -- 'streak', 'completion', 'xp', etc │
│ criteria_value  JSONB NOT NULL  -- threshold or conditions                  │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER_BADGE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ user_id         UUID REFERENCES user(id) ON DELETE CASCADE                  │
│ badge_id        UUID REFERENCES badge(id) ON DELETE CASCADE                 │
│ earned_at       TIMESTAMP DEFAULT NOW()                                     │
│ UNIQUE(user_id, badge_id)                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            XP_TRANSACTION                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ user_id         UUID REFERENCES user(id) ON DELETE CASCADE                  │
│ amount          INTEGER NOT NULL                                            │
│ source_type     VARCHAR(50) NOT NULL  -- 'step', 'bonus', 'challenge'      │
│ source_id       UUID NULL  -- reference to step, challenge, etc             │
│ description     VARCHAR(200) NULL                                           │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANALYTICS_EVENT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ id              UUID PRIMARY KEY                                            │
│ user_id         UUID REFERENCES user(id) ON DELETE SET NULL                 │
│ event_type      VARCHAR(100) NOT NULL  -- 'lesson_started', 'step_completed'│
│ event_data      JSONB NULL                                                  │
│ session_id      UUID NULL                                                   │
│ ip_hash         VARCHAR(64) NULL  -- hashed, not raw IP                     │
│ user_agent      VARCHAR(500) NULL                                           │
│ created_at      TIMESTAMP DEFAULT NOW()                                     │
└─────────────────────────────────────────────────────────────────────────────┘

-- Indexes for performance
CREATE INDEX idx_user_progress_user ON user_progress(user_id);
CREATE INDEX idx_user_progress_lesson ON user_progress(lesson_id);
CREATE INDEX idx_step_completion_user ON step_completion(user_id);
CREATE INDEX idx_xp_transaction_user ON xp_transaction(user_id);
CREATE INDEX idx_analytics_event_type ON analytics_event(event_type);
CREATE INDEX idx_analytics_event_user ON analytics_event(user_id);
CREATE INDEX idx_lesson_module ON lesson(module_id);
CREATE INDEX idx_module_track ON module(track_id);
```

---

## 6. User Flows (V1)

### 6.1 New User Onboarding Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NEW USER ONBOARDING FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

[1] LANDING PAGE
    │
    │  User clicks "Start Learning Free"
    ▼
[2] SIGN UP SCREEN
    │
    │  Options:
    │  • "Continue with Google" → OAuth flow → Skip to [4]
    │  • "Continue with Microsoft" → OAuth flow → Skip to [4]
    │  • Email + Password form → Email verification sent
    │
    ▼
[3] EMAIL VERIFICATION
    │
    │  User clicks link in email
    │  If not verified within 24h, send reminder
    │
    ▼
[4] PROFILE SETUP (30 seconds)
    │
    │  • Enter display name
    │  • Select avatar (8 preset options)
    │  • Set timezone (auto-detected, editable)
    │
    ▼
[5] SKILL ASSESSMENT QUIZ (2-3 minutes)
    │
    │  5-7 questions covering:
    │  • General tech familiarity
    │  • Security awareness basics
    │  • Career goals (defensive/offensive/dev security)
    │
    │  Examples:
    │  Q1: "What does 'phishing' mean to you?"
    │      [ ] A type of fishing  [ ] Email scam  [ ] Network attack
    │  Q2: "Have you ever written code professionally?"
    │      [ ] Yes  [ ] Learning  [ ] No
    │  Q3: "What's your main goal?"
    │      [ ] Career in security  [ ] Secure my code  [ ] General awareness
    │
    ▼
[6] TRACK RECOMMENDATION SCREEN
    │
    │  Based on quiz:
    │  • Beginner → "Cyber Foundations" recommended
    │  • Some tech + dev → "Secure Coding Essentials" recommended
    │  • Some tech + career → "Blue Team Basics" recommended
    │
    │  "We recommend: [Track Name]"
    │  [Start This Track]  [Browse All Tracks]
    │
    ▼
[7] FIRST LESSON LAUNCH
    │
    │  Short intro modal:
    │  "Lessons take 5-15 minutes. Complete one daily to build your streak!"
    │  [Got it, let's go]
    │
    ▼
[8] LESSON PLAYER
    │
    │  User completes first lesson
    │  (Steps: concept → concept → quiz → concept → quiz → code challenge)
    │
    ▼
[9] FIRST COMPLETION CELEBRATION
    │
    │  Modal: "🎉 Lesson Complete!"
    │  • +50 XP earned
    │  • Badge unlocked: "First Step"
    │  • Streak started: 1 day
    │  [Continue to Next Lesson]  [Back to Dashboard]
    │
    ▼
[10] DASHBOARD (now personalized)
     │
     │  Shows:
     │  • "Continue: [Track Name] - [Next Lesson]"
     │  • Streak: 1 day 🔥
     │  • Level 1 (50/100 XP to Level 2)
     │  • Badge shelf with "First Step" badge
```

---

### 6.2 Returning User Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RETURNING USER FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

[1] USER RETURNS TO APP
    │
    │  Check auth state:
    │  • If session valid → [3]
    │  • If session expired → [2]
    │
    ▼
[2] LOGIN SCREEN
    │
    │  • OAuth buttons (Google/Microsoft)
    │  • Email + password
    │  • "Forgot password?" link
    │
    │  After successful auth:
    │  • Update last_login_at
    │  • Generate new session token
    │
    ▼
[3] DASHBOARD
    │
    │  ┌─────────────────────────────────────────┐
    │  │  Welcome back, [Name]!                  │
    │  │                                         │
    │  │  🔥 Streak: 5 days                      │
    │  │                                         │
    │  │  ┌─────────────────────────────────┐   │
    │  │  │ CONTINUE WHERE YOU LEFT OFF     │   │
    │  │  │ [Track] > [Module] > [Lesson]   │   │
    │  │  │ Progress: 60% (Step 4/7)        │   │
    │  │  │         [Resume]                │   │
    │  │  └─────────────────────────────────┘   │
    │  │                                         │
    │  │  Level 3 ████████░░ 280/400 XP         │
    │  │                                         │
    │  │  Recent Badges: [🎖️] [🏆] [⭐]          │
    │  └─────────────────────────────────────────┘
    │
    │  User clicks [Resume]
    │
    ▼
[4] LESSON PLAYER (Resumed)
    │
    │  • Load lesson at saved step (step 4 in this case)
    │  • Previous steps shown as completed (checkmarks)
    │  • User continues from current step
    │
    │  User completes remaining steps
    │
    ▼
[5] LESSON COMPLETION
    │
    │  • Calculate total XP earned
    │  • Check for badge eligibility
    │  • Update streak if needed
    │
    ▼
[6] COMPLETION MODAL
    │
    │  "Lesson Complete!"
    │  • +45 XP earned (varies by steps)
    │  • Streak maintained: 6 days 🔥
    │  • Progress: Module 75% complete
    │
    │  [Next Lesson]  [Back to Dashboard]
    │
    ▼
[7] NEXT LESSON OR DASHBOARD
    │
    │  If [Next Lesson]: Load next lesson in sequence
    │  If [Dashboard]: Return to home, show updated stats
```

---

### 6.3 Lesson Completion & Progress Tracking

#### Step-by-Step Progress Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROGRESS TRACKING INTERNALS                             │
└─────────────────────────────────────────────────────────────────────────────┘

WHEN USER STARTS A LESSON:
────────────────────────────
1. Check if UserProgress record exists for (user_id, lesson_id)
   • If not exists: CREATE with status='in_progress', current_step=0, started_at=NOW()
   • If exists with status='completed': Allow replay, don't overwrite

2. Load all LessonSteps for the lesson, ordered by order_index

3. Render lesson player at current_step index

WHEN USER COMPLETES A STEP:
────────────────────────────
1. Validate answer (if applicable):
   • Quiz: check is_correct against option
   • Code: run validation (regex match or execution)
   • Concept: always "correct" (just read)

2. Calculate XP earned:
   base_xp = step.xp_value (default 10)
   bonus_xp = 0

   IF first_attempt AND is_correct:
       bonus_xp += 5  // first-try bonus

   IF user has active streak >= 7:
       bonus_xp += 2  // streak bonus

   total_xp = base_xp + bonus_xp

3. Record completion:
   INSERT INTO step_completion:
   • user_id, step_id, is_correct, attempts, xp_earned, user_answer, completed_at

   INSERT INTO xp_transaction:
   • user_id, amount=total_xp, source_type='step', source_id=step_id

4. Update user progress:
   UPDATE user_progress SET current_step = current_step + 1

   IF current_step >= total_steps:
       UPDATE user_progress SET status='completed', completed_at=NOW()
       (trigger lesson completion flow)

5. Update gamification profile:
   UPDATE gamification_profile SET total_xp = total_xp + total_xp_earned

   // Check level up
   new_level = calculate_level(new_total_xp)
   IF new_level > current_level:
       UPDATE level = new_level
       (trigger level-up animation)

6. Return to client:
   {
     "step_result": "correct",
     "xp_earned": 15,
     "feedback": "HTTPS uses TLS encryption...",
     "next_step_index": 5,
     "lesson_complete": false
   }

STREAK CALCULATION:
────────────────────
Triggered on any lesson activity (step completion)

1. Get user's gamification_profile.last_activity_date

2. Get user's current date (in their timezone)

3. Logic:
   IF last_activity_date == today:
       // Already active today, no change

   ELSE IF last_activity_date == yesterday:
       // Streak continues
       UPDATE current_streak = current_streak + 1
       UPDATE last_activity_date = today
       IF current_streak > longest_streak:
           UPDATE longest_streak = current_streak

   ELSE:
       // Streak broken (or first activity)
       UPDATE current_streak = 1
       UPDATE last_activity_date = today

4. Check streak badges:
   IF current_streak == 7: Award "Week Warrior" badge
   IF current_streak == 30: Award "Monthly Master" badge
   etc.

BADGE AWARDING:
────────────────
Check badge eligibility after:
• Lesson completion
• Module completion
• Streak updates
• XP milestones

For each unearned badge:
1. Evaluate criteria against user's stats
2. If met, INSERT into user_badge
3. Return badge award to client for celebration UI

Example badge criteria:
{
  "slug": "phishing_spotter",
  "criteria_type": "lessons_completed",
  "criteria_value": {
    "tag": "phishing",
    "count": 5
  }
}
```

---

## 7. Security & Privacy Considerations

### 7.1 Authentication & Access Control

| Control | Implementation |
|---------|----------------|
| **Password Storage** | Argon2id hashing (memory-hard, GPU-resistant). Never store plaintext. |
| **Password Requirements** | Minimum 10 characters. Check against HaveIBeenPwned breached password list via k-anonymity API. |
| **Session Management** | JWT access tokens (15 min expiry) + HTTP-only refresh tokens (7 days). Rotate refresh tokens on use. |
| **OAuth Security** | Validate `state` parameter to prevent CSRF. Verify token signatures. Only request minimal scopes. |
| **Rate Limiting** | Redis-backed sliding window: 100 requests/min per IP for public endpoints, 20 requests/min for auth endpoints. |
| **Brute Force Protection** | Lock account after 5 failed login attempts for 15 minutes. Notify user via email. |
| **CSRF Protection** | SameSite=Strict cookies for sessions. Include CSRF token in state-changing requests. |

### 7.2 API Security

| Control | Implementation |
|---------|----------------|
| **Input Validation** | Use class-validator (NestJS) for all DTOs. Whitelist allowed fields. Sanitize strings. |
| **SQL Injection** | Prisma ORM with parameterized queries. Never interpolate user input into SQL. |
| **XSS Prevention** | React auto-escapes by default. CSP headers with strict-dynamic. Sanitize any HTML in lesson content. |
| **CORS** | Whitelist only our domains. No wildcard origins. |
| **HTTPS Only** | Enforce TLS everywhere. HSTS header with 1-year max-age. |
| **API Versioning** | /api/v1/ prefix. Allows deprecation without breaking clients. |

### 7.3 Code Execution Sandbox (for Code Challenges)

| Control | Implementation |
|---------|----------------|
| **Isolation** | Run in Docker containers with no network access, read-only filesystem. |
| **Resource Limits** | CPU: 0.5 cores max. Memory: 64MB. Execution time: 5 seconds. |
| **No Persistence** | Ephemeral containers destroyed after each execution. |
| **Language Whitelist** | V1: Only bash, Python. Validated syntax before execution. |
| **Output Sanitization** | Strip ANSI codes, limit output to 10KB, escape special characters. |

### 7.4 Data Privacy (GDPR-Ready)

| Principle | Implementation |
|-----------|----------------|
| **Data Minimization** | Only collect: email, display name, timezone, learning progress. No address, phone, employer. |
| **IP Handling** | Hash IPs before storage (SHA-256 with daily salt). Used only for rate limiting and fraud detection. |
| **Right to Export** | API endpoint: GET /api/v1/users/me/export returns all user data as JSON. |
| **Right to Delete** | API endpoint: DELETE /api/v1/users/me triggers cascade delete of all user data. 30-day grace period. |
| **Cookie Consent** | Only essential cookies (auth) without consent. Analytics cookies require opt-in. |
| **Data Encryption** | At rest: Postgres with encrypted volumes. In transit: TLS 1.3 only. |

### 7.5 Audit Logging

```
// Log all security-relevant events

LOGGED EVENTS:
• auth.login.success
• auth.login.failure
• auth.logout
• auth.password.reset.request
• auth.password.reset.complete
• user.created
• user.deleted
• user.email.changed
• user.password.changed
• admin.user.accessed
• admin.content.modified

LOG FORMAT (structured JSON):
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event": "auth.login.failure",
  "user_id": "uuid-or-null",
  "ip_hash": "sha256...",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "email": "user@example.com",
    "reason": "invalid_password",
    "attempt_count": 3
  }
}

RETENTION: 90 days in hot storage, 1 year in cold storage
```

### 7.6 Future Enterprise Security Hooks

Design decisions that enable future enterprise features:

| Future Feature | Current Preparation |
|----------------|---------------------|
| **SSO (Okta/Azure AD)** | OAuth abstraction layer that can accept SAML/OIDC providers. User model has oauth_provider field. |
| **RBAC** | User.role field exists. Guards architecture supports role checking. Can add Role and Permission tables. |
| **Multi-tenancy** | Add organization_id to User and content tables. Filter all queries by org. |
| **Audit Export** | Structured logging format supports export to SIEM. Add API endpoint for enterprise admins. |
| **Data Residency** | Use environment variables for all external service URLs. Can deploy regional instances. |

---

## 8. Roadmap & Milestones

### Phase 0: Prototype (Weeks 1-4)

**Goal**: Validate core learning experience with internal users

#### Key Features
- [ ] Local authentication (email/password only)
- [ ] One complete track: "Cyber Foundations" (5 lessons, ~30 steps)
- [ ] Lesson player supporting: concept, quiz_single, fill_blank
- [ ] Basic XP tracking (no levels or badges yet)
- [ ] Simple dashboard: current lesson, total XP
- [ ] Mobile-responsive design (basic)

#### Implementation Order
1. **Week 1**: Database schema, NestJS scaffolding, basic auth
2. **Week 2**: Content model, lesson loader, lesson player UI
3. **Week 3**: Progress tracking, XP system, dashboard
4. **Week 4**: First track content creation, internal testing

#### Success Criteria
- 10 internal testers complete all 5 lessons
- Average session time > 10 minutes
- No critical bugs blocking lesson completion
- Feedback collected on content quality and UX

#### Tech Debt Accepted
- No OAuth
- No email verification
- Manual content JSON files (no CMS)
- No analytics beyond console logs
- Single environment (local dev only)

---

### Phase 1: Public Beta (Weeks 5-10)

**Goal**: Launch publicly, validate engagement and retention

#### Key Features
- [ ] OAuth (Google, Microsoft)
- [ ] Email verification flow
- [ ] Onboarding skill quiz + track recommendation
- [ ] Three complete tracks: Cyber Foundations, Blue Team Basics, Secure Coding
- [ ] All lesson types implemented (code challenges, scenarios, etc.)
- [ ] Full gamification: levels, streaks, badges
- [ ] Polished dashboard with progress visualization
- [ ] Basic analytics (Mixpanel or PostHog)
- [ ] Deployed to production (Vercel + Railway/Render)

#### Implementation Order
1. **Week 5**: OAuth integration, email verification, production deployment setup
2. **Week 6**: Onboarding flow, track recommendation algorithm
3. **Week 7**: Code challenge execution (regex validation), scenario steps
4. **Week 8**: Gamification: levels, streaks, badge system
5. **Week 9**: Blue Team Basics track content, Secure Coding track content
6. **Week 10**: Analytics integration, performance optimization, beta launch

#### Success Criteria
- 500 beta signups
- 40% complete at least 10 lessons
- 25% maintain 7-day streak
- NPS > 40
- p95 API latency < 200ms
- Zero security incidents

#### Tech Debt Accepted
- No admin CMS (content still in JSON)
- No social features
- No push notifications
- No sandbox code execution (regex validation only)

---

### Phase 2: Growth & Enterprise Readiness (Weeks 11-20)

**Goal**: Scale to thousands of users, prepare for enterprise sales

#### Key Features
- [ ] Admin content management dashboard
- [ ] True code sandbox (Piston integration)
- [ ] Two more tracks (based on beta feedback)
- [ ] Social: friend system, leaderboards
- [ ] Certification path mapping (Security+ domains)
- [ ] Push notifications (web)
- [ ] SSO preparation (SAML/OIDC abstractions)
- [ ] Multi-tenant architecture foundations
- [ ] Enhanced analytics and cohort analysis

#### Implementation Order
1. **Weeks 11-12**: Admin dashboard (content CRUD, user management)
2. **Weeks 13-14**: Piston sandbox integration, advanced code challenges
3. **Weeks 15-16**: Social features (friends, leaderboards)
4. **Weeks 17-18**: New tracks, certification mapping
5. **Weeks 19-20**: SSO preparation, multi-tenant schema migration, enterprise landing page

#### Success Criteria
- 5,000 registered users
- 2 pilot enterprise customers (paid or LOI)
- Content team can create lessons without engineering
- Sandbox executes code safely with 99.9% uptime
- SSO integration works with test Okta/Azure AD instance

#### Tech Debt to Address
- Migrate from JSON content to database-driven CMS
- Add comprehensive integration tests
- Implement proper CI/CD with staging environment
- Add database read replicas if needed

---

### Summary Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPMENT TIMELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 0: PROTOTYPE                                                         │
│  ████████████████                                                           │
│  Weeks 1-4                                                                  │
│  • Core learning loop                                                       │
│  • Internal validation                                                      │
│                                                                             │
│  PHASE 1: PUBLIC BETA                                                       │
│                  ████████████████████████                                   │
│                  Weeks 5-10                                                 │
│                  • Full feature set                                         │
│                  • Public launch                                            │
│                                                                             │
│  PHASE 2: ENTERPRISE READY                                                  │
│                                          ████████████████████████████████   │
│                                          Weeks 11-20                        │
│                                          • Admin tools                      │
│                                          • SSO prep                         │
│                                          • Scale                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Appendix A: Example Lesson Content (JSON)

```json
{
  "id": "lesson-001-what-is-phishing",
  "slug": "what-is-phishing",
  "title": "What is Phishing?",
  "module_id": "module-social-engineering",
  "estimated_mins": 8,
  "xp_reward": 50,
  "steps": [
    {
      "order": 0,
      "type": "concept",
      "content": {
        "title": "The Art of Deception",
        "body": "Phishing is a type of social engineering attack where attackers pretend to be a trusted entity to trick you into revealing sensitive information.\n\nThe name comes from 'fishing' — attackers cast a wide net, hoping someone will bite.",
        "image_url": "/assets/lessons/phishing-intro.svg"
      }
    },
    {
      "order": 1,
      "type": "concept",
      "content": {
        "title": "Common Phishing Tactics",
        "body": "Phishers typically use:\n\n• **Urgency**: \"Your account will be suspended in 24 hours!\"\n• **Authority**: Pretending to be your bank, boss, or IT department\n• **Fear**: \"Suspicious login detected from Russia\"\n• **Reward**: \"You've won a $500 gift card!\"",
        "highlights": ["Urgency", "Authority", "Fear", "Reward"]
      }
    },
    {
      "order": 2,
      "type": "quiz_single",
      "content": {
        "question": "Which of these is a common phishing tactic?",
        "options": [
          {"id": "a", "text": "Sending you a calendar invite", "is_correct": false},
          {"id": "b", "text": "Creating urgency to act quickly", "is_correct": true},
          {"id": "c", "text": "Asking for your username only", "is_correct": false},
          {"id": "d", "text": "Using a .gov email domain", "is_correct": false}
        ],
        "explanation": "Phishers create urgency because it bypasses your rational thinking. When you feel rushed, you're less likely to notice red flags."
      }
    },
    {
      "order": 3,
      "type": "scenario",
      "content": {
        "title": "Spot the Phish",
        "scenario": "You receive this email:\n\n---\n**From:** security@amaz0n-support.com\n**Subject:** URGENT: Verify your account now\n\nDear Customer,\n\nWe detected unusual activity on your account. Click below to verify your identity within 24 hours or your account will be permanently suspended.\n\n[Verify Now]\n\n---",
        "question": "What's the biggest red flag in this email?",
        "options": [
          {"id": "a", "text": "The subject line uses 'URGENT'", "is_correct": false, "feedback": "Urgency is a red flag, but there's an even bigger one here."},
          {"id": "b", "text": "The sender domain is 'amaz0n-support.com' (with a zero)", "is_correct": true, "feedback": "Exactly! The domain uses '0' instead of 'o' to look like Amazon. Always check the sender domain carefully."},
          {"id": "c", "text": "It mentions account suspension", "is_correct": false, "feedback": "This is concerning, but legitimate companies also send suspension warnings. Look closer at the sender."},
          {"id": "d", "text": "It has a 'Verify Now' button", "is_correct": false, "feedback": "Buttons themselves aren't suspicious — it's where they lead that matters. But there's a clearer red flag."}
        ]
      }
    },
    {
      "order": 4,
      "type": "fill_blank",
      "content": {
        "instruction": "Complete the security advice:",
        "template": "Before clicking any link in an email, hover over it to check the actual ___.",
        "answer": "URL",
        "alternatives": ["url", "link", "address", "destination"],
        "explanation": "Hovering over links reveals their true destination. Phishing emails often display 'amazon.com' but actually link to 'evil-site.com/amazon'."
      }
    },
    {
      "order": 5,
      "type": "concept",
      "content": {
        "title": "Key Takeaways",
        "body": "✓ Phishing exploits human psychology, not technical vulnerabilities\n\n✓ Always verify sender domains character by character\n\n✓ Hover over links before clicking\n\n✓ When in doubt, go directly to the website instead of clicking email links",
        "style": "summary"
      }
    },
    {
      "order": 6,
      "type": "quiz_single",
      "content": {
        "question": "Your CEO emails asking you to urgently buy gift cards and send the codes. What should you do?",
        "options": [
          {"id": "a", "text": "Buy the gift cards — it's the CEO!", "is_correct": false},
          {"id": "b", "text": "Reply to the email asking for confirmation", "is_correct": false},
          {"id": "c", "text": "Call or message the CEO through a different channel to verify", "is_correct": true},
          {"id": "d", "text": "Forward the email to IT and wait", "is_correct": false}
        ],
        "explanation": "This is 'CEO fraud' or 'business email compromise.' Never reply to the suspicious email — contact the person through a completely different channel (phone, Slack, in person) to verify."
      }
    }
  ]
}
```

---

## Appendix B: API Endpoints (V1)

### Authentication
```
POST   /api/v1/auth/register          # Email/password registration
POST   /api/v1/auth/login             # Email/password login
POST   /api/v1/auth/logout            # Invalidate session
POST   /api/v1/auth/refresh           # Refresh access token
GET    /api/v1/auth/oauth/google      # Initiate Google OAuth
GET    /api/v1/auth/oauth/google/callback
GET    /api/v1/auth/oauth/microsoft   # Initiate Microsoft OAuth
GET    /api/v1/auth/oauth/microsoft/callback
POST   /api/v1/auth/password/reset    # Request password reset
POST   /api/v1/auth/password/reset/confirm
POST   /api/v1/auth/email/verify      # Verify email with token
```

### Users
```
GET    /api/v1/users/me               # Current user profile
PATCH  /api/v1/users/me               # Update profile
DELETE /api/v1/users/me               # Delete account
GET    /api/v1/users/me/export        # GDPR data export
```

### Content
```
GET    /api/v1/tracks                 # List all tracks
GET    /api/v1/tracks/:slug           # Get track with modules
GET    /api/v1/modules/:id            # Get module with lessons
GET    /api/v1/lessons/:id            # Get lesson with steps
```

### Progress
```
GET    /api/v1/progress               # All user progress
GET    /api/v1/progress/tracks/:id    # Progress for specific track
POST   /api/v1/progress/lessons/:id/start    # Start a lesson
POST   /api/v1/progress/steps/:id/complete   # Complete a step
GET    /api/v1/progress/current       # Get current/resume point
```

### Gamification
```
GET    /api/v1/gamification/profile   # XP, level, streak
GET    /api/v1/gamification/badges    # All badges (earned + locked)
GET    /api/v1/gamification/leaderboard  # Top users (V1.5)
```

### Onboarding
```
POST   /api/v1/onboarding/quiz        # Submit skill assessment
GET    /api/v1/onboarding/recommendation  # Get track recommendation
POST   /api/v1/onboarding/complete    # Mark onboarding done
```

### Code Execution (V1.5)
```
POST   /api/v1/execute                # Run code in sandbox
       Body: { language: "python", code: "...", timeout: 5000 }
       Response: { stdout: "...", stderr: "...", exit_code: 0 }
```

---

## Appendix C: Environment Variables

```bash
# Application
NODE_ENV=production
PORT=3000
API_URL=https://api.cyberlearn.app
WEB_URL=https://cyberlearn.app

# Database
DATABASE_URL=postgresql://user:pass@host:5432/cyberlearn

# Redis
REDIS_URL=redis://host:6379

# Auth
JWT_SECRET=<random-256-bit-key>
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d
SESSION_SECRET=<random-256-bit-key>

# OAuth - Google
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_CALLBACK_URL=https://api.cyberlearn.app/api/v1/auth/oauth/google/callback

# OAuth - Microsoft
MICROSOFT_CLIENT_ID=xxx
MICROSOFT_CLIENT_SECRET=xxx
MICROSOFT_CALLBACK_URL=https://api.cyberlearn.app/api/v1/auth/oauth/microsoft/callback

# Email (SendGrid/Postmark)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=xxx
EMAIL_FROM=learn@cyberlearn.app

# Storage (S3/R2)
STORAGE_PROVIDER=r2
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY=xxx
R2_SECRET_KEY=xxx
R2_BUCKET=cyberlearn-assets

# Analytics (PostHog)
POSTHOG_API_KEY=xxx
POSTHOG_HOST=https://app.posthog.com

# Code Execution (Piston)
PISTON_URL=http://piston:2000

# Feature Flags
FEATURE_CODE_SANDBOX=false
FEATURE_SOCIAL=false
FEATURE_PUSH_NOTIFICATIONS=false
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Authors: Product & Engineering Team*
