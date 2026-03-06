# CV Grading – Frontend Integration

## Step 1: API Base URL

Create a config or constant (adjust for your setup):

```javascript
// src/config.js or src/api/config.js
export const API_BASE_URL = 'http://localhost:8000';
```

---

## Step 2: API Service Function

```javascript
// src/api/cvApi.js

const API_BASE = 'http://localhost:8000';

export async function gradeCV(cvText) {
  const res = await fetch(`${API_BASE}/api/cv/grade/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_text: cvText }),
  });
  if (!res.ok) throw new Error('Failed to grade CV');
  return res.json();
}

export async function gradeCVFromFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/cv/grade/`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to grade CV');
  return res.json();
}
```

---

## Step 3: Full React Component

Copy this into your project (e.g. `src/pages/CVGrader.jsx` or `src/components/CVGrader.jsx`):

```jsx
import { useState } from 'react';

const API_BASE = 'http://localhost:8000';

export default function CVGrader() {
  const [cvText, setCvText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputMode, setInputMode] = useState('text'); // 'text' or 'file'

  const handleGradeFromText = async () => {
    if (!cvText.trim()) {
      setError('Please enter or paste your CV text');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/cv/grade/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cvText }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleGradeFromFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().match(/\.(pdf|docx|doc)$/)) {
      setError('Please upload a PDF or DOCX file');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE}/api/cv/grade/`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'Excellent': return '#22c55e';
      case 'Good': return '#3b82f6';
      case 'Average': return '#f59e0b';
      case 'Poor': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
      <h1>CV / Resume Grader</h1>
      <p>Paste your CV text or upload a PDF/DOCX to get a score and improvement suggestions.</p>

      {/* Input mode toggle */}
      <div style={{ marginBottom: 16 }}>
        <button
          onClick={() => setInputMode('text')}
          style={{
            padding: '8px 16px',
            marginRight: 8,
            background: inputMode === 'text' ? '#3b82f6' : '#e5e7eb',
            color: inputMode === 'text' ? 'white' : '#374151',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
          }}
        >
          Paste Text
        </button>
        <button
          onClick={() => setInputMode('file')}
          style={{
            padding: '8px 16px',
            background: inputMode === 'file' ? '#3b82f6' : '#e5e7eb',
            color: inputMode === 'file' ? 'white' : '#374151',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
          }}
        >
          Upload File
        </button>
      </div>

      {inputMode === 'text' ? (
        <>
          <textarea
            value={cvText}
            onChange={(e) => setCvText(e.target.value)}
            placeholder="Paste your CV or resume text here..."
            rows={12}
            style={{
              width: '100%',
              padding: 12,
              borderRadius: 8,
              border: '1px solid #d1d5db',
              fontSize: 14,
              marginBottom: 16,
            }}
          />
          <button
            onClick={handleGradeFromText}
            disabled={loading}
            style={{
              padding: '12px 24px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: 8,
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: 16,
            }}
          >
            {loading ? 'Grading...' : 'Grade CV'}
          </button>
        </>
      ) : (
        <div style={{ marginBottom: 16 }}>
          <input
            type="file"
            accept=".pdf,.docx,.doc"
            onChange={handleGradeFromFile}
            disabled={loading}
            style={{ marginBottom: 8 }}
          />
          {loading && <p>Processing...</p>}
        </div>
      )}

      {error && (
        <div style={{ padding: 12, background: '#fef2f2', color: '#dc2626', borderRadius: 8, marginTop: 16 }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 32, padding: 24, background: '#f9fafb', borderRadius: 12, border: '1px solid #e5e7eb' }}>
          <h2 style={{ marginTop: 0 }}>Results</h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: getGradeColor(result.grade),
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 28,
                fontWeight: 'bold',
              }}
            >
              {result.score}
            </div>
            <div>
              <div style={{ fontSize: 24, fontWeight: 600, color: getGradeColor(result.grade) }}>
                {result.grade}
              </div>
              <div style={{ color: '#6b7280' }}>Score: {result.score}/100</div>
            </div>
          </div>

          {result.suggestions?.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <h3>Improvement Suggestions</h3>
              <ul style={{ paddingLeft: 20, margin: 0 }}>
                {result.suggestions.map((s, i) => (
                  <li key={i} style={{ marginBottom: 8 }}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          {result.enhanced_resume && (
            <div>
              <h3>Enhanced Resume</h3>
              <textarea
                readOnly
                value={result.enhanced_resume}
                rows={15}
                style={{
                  width: '100%',
                  padding: 12,
                  borderRadius: 8,
                  border: '1px solid #d1d5db',
                  fontSize: 14,
                  fontFamily: 'inherit',
                }}
              />
              <button
                onClick={() => navigator.clipboard.writeText(result.enhanced_resume)}
                style={{
                  marginTop: 8,
                  padding: '8px 16px',
                  background: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: 8,
                  cursor: 'pointer',
                }}
              >
                Copy to Clipboard
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Step 4: Add Route

**React Router:**

```jsx
import CVGrader from './pages/CVGrader';

// In your routes:
<Route path="/cv-grade" element={<CVGrader />} />
// or
<Route path="/grade-cv" element={<CVGrader />} />
```

**Next.js (App Router):**

Create `app/cv-grade/page.jsx` and paste the component there.

---

## Step 5: CORS (Backend)

In `backend/settings.py`, ensure your frontend URL is allowed:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
]
```

---

## Troubleshooting: "Nothing happens" when uploading PDF

### 1. Use the correct form field name
The backend accepts: `file`, `resume`, `cv`, `cv_file`, or `document`. Use one of these:

```javascript
formData.append('file', file);  // ✅ Recommended
```

### 2. Trigger the API on file select
You must call the API when the user selects a file. Use `onChange`:

```jsx
<input
  type="file"
  accept=".pdf,.docx,.doc"
  onChange={handleGradeFromFile}  // Must call API here
/>
```

### 3. Handle errors and show loading state
```javascript
try {
  setLoading(true);
  const res = await fetch(...);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  setResult(data);
} catch (err) {
  setError(err.message);  // Show this to the user!
} finally {
  setLoading(false);
}
```

### 4. Check backend is running
```bash
cd Back_Back && python manage.py runserver
```

### 5. Test with curl
```bash
curl -X POST http://localhost:8000/api/cv/grade/ \
  -F "file=@/path/to/your/resume.pdf"
```

---

## Step 6: Run Both

```bash
# Terminal 1 - Backend
cd Back_Back && python manage.py runserver

# Terminal 2 - Frontend (Vite/React)
npm run dev
```

Then open `http://localhost:5173/cv-grade` (or your route).

---

## Quick Checklist

| Step | Action |
|------|--------|
| 1 | Add `CVGrader` component to your project |
| 2 | Add route (e.g. `/cv-grade`) |
| 3 | Set `API_BASE` to your backend URL |
| 4 | Add frontend origin to Django `CORS_ALLOWED_ORIGINS` |
| 5 | Start backend and frontend |

---

## Response Shape

```typescript
interface GradeResult {
  score: number;           // 0-100
  grade: 'Poor' | 'Average' | 'Good' | 'Excellent';
  needs_enhancement: boolean;
  suggestions?: string[];
  missing_sections?: string[];
  enhanced_resume?: string;
}
```
