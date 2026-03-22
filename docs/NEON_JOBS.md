# Viewing jobs (and related data) in Neon

Your Django app stores jobs in **PostgreSQL** — when `DATABASE_URL` points to Neon, all job data lives in your Neon project.

## If `SELECT * FROM jobs` returns no rows

1. **Neon vs local DB** — If `.env` does not set `DATABASE_URL` to Neon, your Django `runserver` / `seed_jobs` may be writing to **SQLite** (`db.sqlite3`) or another DB, while Neon stays empty. Fix: set `DATABASE_URL` to your Neon connection string, run `python manage.py migrate`, then `python manage.py seed_jobs`.

2. **Or insert directly in Neon** — Open **`docs/seed_jobs_neon.sql`**, copy all SQL into Neon **SQL Editor**, and **Run**. That inserts 4 sample jobs with `created_by_id` NULL (valid for your schema).

## Open the SQL Editor

1. Go to [Neon Console](https://console.neon.tech) → your project → **SQL Editor**.
2. Select database **`neondb`** (or the DB name from your connection string).

## Useful queries

**All job postings (main fields):**

```sql
SELECT
  id,
  job_title,
  company_name,
  location,
  employment_type,
  status,
  is_remote,
  application_deadline,
  contact_email,
  salary_min,
  salary_max,
  created_at
FROM jobs
ORDER BY created_at DESC;
```

**Full text fields (description, responsibilities, requirements):**

```sql
SELECT
  job_title,
  job_description,
  key_responsibilities,
  requirements,
  preferred_qualifications,
  benefits_perks,
  years_of_experience
FROM jobs
ORDER BY created_at DESC
LIMIT 10;
```

**Skills linked to jobs** (Django M2M table `jobs_job_skills`):

```sql
SELECT j.job_title, s.name AS skill
FROM jobs j
JOIN jobs_job_skills js ON js.job_id = j.id
JOIN skills s ON s.id = js.skill_id
ORDER BY j.job_title, s.name;
```

**Count jobs by status:**

```sql
SELECT status, COUNT(*) FROM jobs GROUP BY status;
```

## Table names (Django)

| Concept        | Table name        |
|----------------|-------------------|
| Job            | `jobs`            |
| Skill          | `skills`          |
| Job ↔ Skill    | `jobs_job_skills` |
| Job application| `job_applications`|

## After running `seed_jobs`

Run in your backend folder:

```bash
python manage.py seed_jobs
# or replace existing sample rows:
python manage.py seed_jobs --force
```

Then refresh Neon SQL Editor and run `SELECT * FROM jobs;` to see the new rows.
