"""Insert rich sample job rows (idempotent; use --force to replace by title)."""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from jobs.models import Job, Skill

User = get_user_model()

SAMPLES = [
    {
        "job_title": "Frontend Developer (React)",
        "company_name": "Ansari Tech",
        "location": "Kathmandu, Nepal",
        "employment_type": "full_time",
        "job_description": (
            "We are building the next generation of career tools for job seekers across South Asia. "
            "You will own features end-to-end: from Figma handoff to production deploy. Our stack is "
            "React 18, Vite, Tailwind CSS, and REST APIs backed by Django. You will participate in "
            "code reviews, write tests, and help shape our component library."
        ),
        "application_deadline": date.today() + timedelta(days=30),
        "contact_email": "careers@ansaritech.example",
        "salary_min": 80000,
        "salary_max": 120000,
        "is_remote": True,
        "key_responsibilities": (
            "- Implement responsive layouts and reusable UI components.\n"
            "- Integrate with REST APIs and handle loading/error states.\n"
            "- Improve performance (lazy loading, memoization, bundle size).\n"
            "- Collaborate with designers on accessibility and UX polish."
        ),
        "requirements": (
            "2+ years professional experience with React.\n"
            "Solid JavaScript (ES6+) and HTML/CSS fundamentals.\n"
            "Experience with Git and modern build tools (Vite or Webpack).\n"
            "Good communication skills in English."
        ),
        "preferred_qualifications": (
            "TypeScript experience.\n"
            "Familiarity with React Router and state management (Context/Zustand).\n"
            "Basic understanding of WCAG accessibility guidelines."
        ),
        "years_of_experience": "2–5 years",
        "benefits_perks": (
            "Health insurance, learning budget (courses/books), flexible hours, remote-friendly, "
            "annual team retreat, performance bonuses."
        ),
        "status": "active",
        "skills": ["React", "JavaScript", "Tailwind CSS", "TypeScript"],
    },
    {
        "job_title": "Backend Engineer (Django)",
        "company_name": "Cloud Nepal",
        "location": "Remote (Nepal time zones)",
        "employment_type": "contract",
        "job_description": (
            "Join our platform team maintaining high-traffic APIs and background workers. You will "
            "work with Django REST Framework, PostgreSQL on Neon, JWT auth, and CI/CD. Expect to "
            "debug production issues, write migrations, and document endpoints for frontend engineers."
        ),
        "application_deadline": date.today() + timedelta(days=21),
        "contact_email": "hr@cloudnepal.example",
        "salary_min": 70000,
        "salary_max": 100000,
        "is_remote": True,
        "key_responsibilities": (
            "- Design and maintain RESTful APIs with DRF.\n"
            "- Optimize queries, indexes, and connection pooling.\n"
            "- Implement secure authentication and permission classes.\n"
            "- Participate in on-call rotation for critical incidents (light)."
        ),
        "requirements": (
            "3+ years Python; 2+ years Django in production.\n"
            "PostgreSQL (migrations, explain plans, transactions).\n"
            "Experience with Docker and environment-based configuration."
        ),
        "preferred_qualifications": (
            "Experience with Neon, AWS, or similar cloud Postgres.\n"
            "Familiarity with pytest and API contract testing."
        ),
        "years_of_experience": "3+ years",
        "benefits_perks": (
            "Contract rate paid monthly, hardware stipend, flexible schedule, optional extension."
        ),
        "status": "active",
        "skills": ["Python", "Django", "PostgreSQL", "Docker"],
    },
    {
        "job_title": "Data Analyst Intern",
        "company_name": "Retail Analytics Co.",
        "location": "Pokhara",
        "employment_type": "internship",
        "job_description": (
            "Six-month internship supporting our analytics squad. You will extract insights from "
            "sales and inventory data, build Excel/Power BI reports, and learn SQL in a mentored "
            "environment. Ideal for recent graduates in statistics, business, or CS."
        ),
        "application_deadline": date.today() + timedelta(days=14),
        "contact_email": "interns@retailanalytics.example",
        "is_remote": False,
        "salary_min": 15000,
        "salary_max": 25000,
        "key_responsibilities": (
            "- Run weekly KPI reports and validate data quality.\n"
            "- Assist with ad-hoc SQL queries and spreadsheet models.\n"
            "- Present findings in short stand-ups with your mentor."
        ),
        "requirements": (
            "Bachelor’s (ongoing or completed) in a quantitative field.\n"
            "Strong Excel skills; willingness to learn SQL.\n"
            "Good attention to detail and documentation habits."
        ),
        "preferred_qualifications": (
            "Coursework or projects in Python or R.\n"
            "Interest in retail or supply chain analytics."
        ),
        "years_of_experience": "0–1 year (internship)",
        "benefits_perks": (
            "Monthly stipend, certificate on completion, lunch on office days, mentorship from senior analysts."
        ),
        "status": "active",
        "skills": ["SQL", "Excel", "Python"],
    },
    {
        "job_title": "DevOps / Site Reliability (Junior)",
        "company_name": "Ansari Tech",
        "location": "Kathmandu (hybrid)",
        "employment_type": "full_time",
        "job_description": (
            "Help us keep our production stack healthy: CI pipelines, monitoring, backups, and "
            "incident response. You will work closely with backend engineers to automate deploys and "
            "reduce mean time to recovery."
        ),
        "application_deadline": date.today() + timedelta(days=45),
        "contact_email": "platform@ansaritech.example",
        "salary_min": 55000,
        "salary_max": 85000,
        "is_remote": False,
        "key_responsibilities": (
            "- Maintain GitHub Actions / CI workflows.\n"
            "- Monitor uptime and logs; document runbooks.\n"
            "- Assist with SSL, DNS, and secrets rotation."
        ),
        "requirements": (
            "1+ year Linux shell experience.\n"
            "Basic networking (HTTP, DNS, TLS).\n"
            "Scripting in Bash or Python."
        ),
        "preferred_qualifications": (
            "Docker or Kubernetes exposure.\n"
            "Interest in observability (Prometheus, Grafana, or similar)."
        ),
        "years_of_experience": "1–3 years",
        "benefits_perks": "Hybrid schedule, learning budget, health coverage after probation.",
        "status": "active",
        "skills": ["Linux", "Docker", "CI/CD", "Python"],
    },
    {
        "job_title": "Mobile Developer (Flutter)",
        "company_name": "Pocket Apps Nepal",
        "location": "Lalitpur",
        "employment_type": "full_time",
        "job_description": (
            "Ship cross-platform mobile apps for fintech and education clients. You will work with "
            "Flutter, REST APIs, and app store release processes. Small agile team with code review "
            "and pair programming."
        ),
        "application_deadline": date.today() + timedelta(days=28),
        "contact_email": "mobile@pocketapps.example",
        "salary_min": 65000,
        "salary_max": 95000,
        "is_remote": True,
        "key_responsibilities": (
            "- Build and maintain Flutter screens and state management.\n"
            "- Integrate secure auth and payment SDKs where required.\n"
            "- Fix crashes and performance issues from production analytics."
        ),
        "requirements": "1+ years Flutter or strong native mobile background; Dart basics; Git.",
        "preferred_qualifications": "Firebase; push notifications; basic CI for mobile builds.",
        "years_of_experience": "1–4 years",
        "benefits_perks": "EPF, festival bonuses, device allowance, hybrid work.",
        "status": "active",
        "skills": ["Flutter", "Dart", "Firebase", "REST APIs"],
    },
    {
        "job_title": "UX/UI Designer",
        "company_name": "Creative Studio Kathmandu",
        "location": "Kathmandu",
        "employment_type": "full_time",
        "job_description": (
            "Design web and mobile experiences for startups and NGOs. You will translate briefs into "
            "wireframes, high-fidelity mockups in Figma, and hand off specs to developers."
        ),
        "application_deadline": date.today() + timedelta(days=35),
        "contact_email": "design@csk.example",
        "salary_min": 45000,
        "salary_max": 75000,
        "is_remote": False,
        "key_responsibilities": (
            "- Run discovery workshops and user flows.\n"
            "- Maintain design system and component library.\n"
            "- Collaborate with PMs and engineers in weekly sprints."
        ),
        "requirements": "Portfolio required; 2+ years Figma; understanding of responsive layouts.",
        "preferred_qualifications": "Basic HTML/CSS awareness; motion design; accessibility basics.",
        "years_of_experience": "2+ years",
        "benefits_perks": "Creative Fridays, conference budget, health insurance.",
        "status": "active",
        "skills": ["Figma", "UI Design", "Prototyping", "User Research"],
    },
    {
        "job_title": "QA Engineer (Automation)",
        "company_name": "Quality First QA",
        "location": "Remote",
        "employment_type": "contract",
        "job_description": (
            "Automate regression suites for SaaS products using Playwright or Cypress. You will triage "
            "bugs, write test plans, and integrate tests into CI pipelines."
        ),
        "application_deadline": date.today() + timedelta(days=20),
        "contact_email": "qa@qualityfirst.example",
        "salary_min": 60000,
        "salary_max": 90000,
        "is_remote": True,
        "key_responsibilities": (
            "- Design and implement E2E and API tests.\n"
            "- Report and track defects in Jira.\n"
            "- Improve test coverage and flake reduction."
        ),
        "requirements": "Experience with test automation; JavaScript or Python; CI basics.",
        "preferred_qualifications": "Performance testing; accessibility testing; Docker.",
        "years_of_experience": "2+ years",
        "benefits_perks": "Remote-first, flexible hours, hourly or monthly contract.",
        "status": "active",
        "skills": ["Playwright", "JavaScript", "CI/CD", "Jira"],
    },
    {
        "job_title": "Digital Marketing Specialist",
        "company_name": "Growth Nepal Digital",
        "location": "Kathmandu",
        "employment_type": "full_time",
        "job_description": (
            "Run paid campaigns (Meta, Google Ads), SEO, and content calendars for local and regional "
            "brands. Report weekly on CPL, ROAS, and organic traffic."
        ),
        "application_deadline": date.today() + timedelta(days=25),
        "contact_email": "careers@growthnepal.example",
        "salary_min": 35000,
        "salary_max": 55000,
        "is_remote": False,
        "key_responsibilities": (
            "- Plan and optimize ad spend across channels.\n"
            "- Coordinate with designers for creatives.\n"
            "- Use GA4 and Search Console for reporting."
        ),
        "requirements": "1+ year hands-on ads; strong English/Nepali copy; analytical mindset.",
        "preferred_qualifications": "Google Ads certification; experience with Nepali e-commerce brands.",
        "years_of_experience": "1–3 years",
        "benefits_perks": "Performance bonuses, team outings, skill workshops.",
        "status": "active",
        "skills": ["Google Ads", "Meta Ads", "SEO", "Analytics"],
    },
    {
        "job_title": "Cybersecurity Analyst",
        "company_name": "SecureNet Nepal",
        "location": "Biratnagar",
        "employment_type": "full_time",
        "job_description": (
            "Monitor SIEM alerts, conduct vulnerability assessments, and support incident response for "
            "enterprise clients. Rotating on-call with senior analysts."
        ),
        "application_deadline": date.today() + timedelta(days=40),
        "contact_email": "soc@securenet.example",
        "salary_min": 70000,
        "salary_max": 110000,
        "is_remote": False,
        "key_responsibilities": (
            "- Triage alerts and document incidents.\n"
            "- Run quarterly phishing simulations.\n"
            "- Assist with policy and hardening checklists."
        ),
        "requirements": "Networking and OS fundamentals; curiosity for blue team work; shift flexibility.",
        "preferred_qualifications": "Security+ or CEH; experience with Splunk/Elastic.",
        "years_of_experience": "2+ years",
        "benefits_perks": "Certification sponsorship, on-call allowance, insurance.",
        "status": "active",
        "skills": ["SIEM", "Networking", "Linux", "Incident Response"],
    },
    {
        "job_title": "Full Stack Developer (MERN)",
        "company_name": "StartupLab Asia",
        "location": "Remote",
        "employment_type": "freelance",
        "job_description": (
            "Build MVPs for early-stage founders: MongoDB, Express, React, Node. Fast iterations, "
            "clear demos, and handover documentation. Project-based with possible extension."
        ),
        "application_deadline": date.today() + timedelta(days=18),
        "contact_email": "build@startuplab.example",
        "salary_min": 90000,
        "salary_max": 140000,
        "is_remote": True,
        "key_responsibilities": (
            "- Scaffold APIs and React dashboards per spec.\n"
            "- Deploy to Vercel/Railway or similar.\n"
            "- Weekly demos with stakeholders."
        ),
        "requirements": "Solid MERN stack; portfolio of shipped apps; good async communication.",
        "preferred_qualifications": "TypeScript; Next.js; Stripe integration.",
        "years_of_experience": "3+ years",
        "benefits_perks": "Hourly/project rates; flexible schedule; referral bonuses.",
        "status": "active",
        "skills": ["MongoDB", "Express", "React", "Node.js"],
    },
    {
        "job_title": "Technical Writer (API Docs)",
        "company_name": "Docs & Co.",
        "location": "Remote",
        "employment_type": "part_time",
        "job_description": (
            "Write and maintain OpenAPI specs, developer guides, and changelog entries for B2B APIs. "
            "Work with engineers to turn endpoints into clear tutorials."
        ),
        "application_deadline": date.today() + timedelta(days=22),
        "contact_email": "writers@docsco.example",
        "salary_min": 25000,
        "salary_max": 40000,
        "is_remote": True,
        "key_responsibilities": (
            "- Produce Markdown/MkDocs or similar documentation sites.\n"
            "- Review PRs that affect public API contracts.\n"
            "- Run doc usability tests with partner developers."
        ),
        "requirements": "Excellent English; experience documenting software; attention to detail.",
        "preferred_qualifications": "Familiarity with REST/JSON; prior OpenAPI work.",
        "years_of_experience": "1+ years",
        "benefits_perks": "Part-time hours, async-friendly, annual contract renewal.",
        "status": "active",
        "skills": ["Technical Writing", "Markdown", "OpenAPI", "REST"],
    },
    {
        "job_title": "HR & Talent Partner",
        "company_name": "Ansari Tech",
        "location": "Kathmandu",
        "employment_type": "full_time",
        "job_description": (
            "Own full-cycle recruiting for engineering and product roles. Partner with hiring "
            "managers on job descriptions, sourcing, interviews, and offers while improving candidate "
            "experience."
        ),
        "application_deadline": date.today() + timedelta(days=32),
        "contact_email": "people@ansaritech.example",
        "salary_min": 40000,
        "salary_max": 65000,
        "is_remote": False,
        "key_responsibilities": (
            "- Source via LinkedIn, communities, and referrals.\n"
            "- Coordinate interview panels and feedback.\n"
            "- Support onboarding and employer branding initiatives."
        ),
        "requirements": "2+ years tech recruiting or HR generalist with tech exposure; strong communicator.",
        "preferred_qualifications": "Experience with ATS; knowledge of Nepal labor law basics.",
        "years_of_experience": "2–5 years",
        "benefits_perks": "Hybrid office, learning stipend, team events.",
        "status": "active",
        "skills": ["Recruiting", "ATS", "Interviewing", "Employer Branding"],
    },
]


class Command(BaseCommand):
    help = "Create rich sample jobs. Skips titles that already exist unless --force."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete existing rows whose job_title matches a sample, then recreate them.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        staff = User.objects.filter(is_staff=True).first()

        if force:
            titles = [s["job_title"] for s in SAMPLES]
            deleted, _ = Job.objects.filter(job_title__in=titles).delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f"Removed {deleted} existing object(s) for sample titles."))

        created = 0
        skipped = 0
        for sample in SAMPLES:
            data = {k: v for k, v in sample.items() if k != "skills"}
            skill_names = sample.get("skills", [])
            if Job.objects.filter(job_title=data["job_title"]).exists():
                self.stdout.write(f"Skip (exists): {data['job_title']}")
                skipped += 1
                continue
            job = Job.objects.create(created_by=staff, **data)
            for name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=name)
                job.skills.add(skill)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Created job: {job.job_title}"))

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created: {created}, skipped (already there): {skipped}")
        )
        self.stdout.write(
            "View rows in Neon: SQL Editor → run SELECT * FROM jobs; (see docs/NEON_JOBS.md)."
        )
