# Frontend Guide: CV Grading & Enhancement

## Backend API Endpoints

Base URL: `http://localhost:8000` (or your deployed backend URL)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cv/grade/` | POST | Grade + enhance (full result) |
| `/api/cv/grade-only/` | POST | Grade only (score, grade) |
| `/api/cv/enhance/` | POST | Enhancement suggestions only |

---

## 1. Grade & Enhance (Main Endpoint)

**POST** `/api/cv/grade/`

### Option A: Send CV text (JSON)

```javascript
const response = await fetch('http://localhost:8000/api/cv/grade/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    cv_text: "John Doe\nSoftware Engineer with 5 years experience. Skills: Python, Java, React..."
  }),
});
const result = await response.json();
```

### Option B: Upload PDF or DOCX file

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]); // PDF or DOCX

const response = await fetch('http://localhost:8000/api/cv/grade/', {
  method: 'POST',
  body: formData,
});
const result = await response.json();
```

### Response

```json
{
  "score": 72,
  "grade": "Average",
  "needs_enhancement": true,
  "suggestions": [
    "ADD: Missing sections - summary",
    "IMPROVE: Replace 'did' with 'Executed'",
    "ADD: Include quantitative achievements..."
  ],
  "missing_sections": ["summary"],
  "enhanced_resume": "...enhanced text with template sections..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| score | number | 0–100 |
| grade | string | "Poor", "Average", "Good", "Excellent" |
| needs_enhancement | boolean | Whether suggestions were generated |
| suggestions | array | Improvement tips |
| missing_sections | array | Sections to add |
| enhanced_resume | string | Enhanced version (when needs_enhancement) |

---

## 2. Grade Only

**POST** `/api/cv/grade-only/`

```javascript
const response = await fetch('http://localhost:8000/api/cv/grade-only/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ cv_text: "Your resume text..." }),
});
const { score, grade, needs_enhancement } = await response.json();
```

---

## 3. Enhance Only

**POST** `/api/cv/enhance/`

```javascript
const response = await fetch('http://localhost:8000/api/cv/enhance/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ cv_text: "Your resume text..." }),
});
const { enhanced_resume, suggestions, missing_sections } = await response.json();
```

---

## React Example

```jsx
import { useState } from 'react';

function CVGrader() {
  const [cvText, setCvText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGrade = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/cv/grade/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cvText }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: err.message });
    }
    setLoading(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('http://localhost:8000/api/cv/grade/', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: err.message });
    }
    setLoading(false);
  };

  return (
    <div>
      <textarea
        value={cvText}
        onChange={(e) => setCvText(e.target.value)}
        placeholder="Paste your CV text..."
        rows={10}
      />
      <button onClick={handleGrade} disabled={loading}>Grade CV</button>
      <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} />

      {result && (
        <div>
          <h3>Score: {result.score}/100 - {result.grade}</h3>
          {result.suggestions?.length > 0 && (
            <ul>
              {result.suggestions.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          )}
          {result.enhanced_resume && (
            <pre>{result.enhanced_resume}</pre>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## CORS

Ensure your backend allows your frontend origin. In Django `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite
]
```

---

## Grade Levels

| Score | Grade |
|-------|-------|
| &lt; 65 | Poor |
| 65–75 | Average |
| 75–82 | Good |
| &gt; 82 | Excellent |
