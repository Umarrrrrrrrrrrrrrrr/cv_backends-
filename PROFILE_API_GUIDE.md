# Profile API – Frontend Integration

## Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/auth/profile/` or `/api/profile/` | Bearer token | Get current user profile |
| PUT | `/api/auth/profile/` or `/api/profile/` | Bearer token | Update profile (full) |
| PATCH | `/api/auth/profile/` or `/api/profile/` | Bearer token | Update profile (partial) |

---

## Get Profile

```javascript
const res = await fetch('http://localhost:8000/api/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
});
const { user } = await res.json();
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "umar@gmail.com",
    "username": "umar",
    "first_name": "umar",
    "last_name": "",
    "full_name": "umar",
    "phone": "+1 234 567 8000",
    "location": "Dry Country",
    "bio": "",
    "linkedin_url": "",
    "website_url": "",
    "profile_photo": null,
    "profile_photo_url": null,
    "role": "user",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

---

## Update Profile (JSON)

```javascript
const res = await fetch('http://localhost:8000/api/auth/profile/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    full_name: 'Umar Ansari',      // or first_name, last_name
    username: 'umar',
    phone: '+1 234 567 8000',
    location: 'Dry Country',
    bio: 'Tell us about yourself..',
    linkedin_url: 'https://linkedin.com/in/yourprofile',
    website_url: 'https://yourwebsite.com',
  }),
});
const { user } = await res.json();
```

---

## Update Profile with Photo (FormData)

```javascript
const formData = new FormData();
formData.append('full_name', 'Umar Ansari');
formData.append('username', 'umar');
formData.append('phone', '+1 234 567 8000');
formData.append('location', 'Dry Country');
formData.append('bio', 'Tell us about yourself..');
formData.append('linkedin_url', 'https://linkedin.com/in/yourprofile');
formData.append('website_url', 'https://yourwebsite.com');
formData.append('profile_photo', fileInput.files[0]);  // Image file

const res = await fetch('http://localhost:8000/api/auth/profile/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData,
});
```

**Note:** Do NOT set `Content-Type` when sending FormData; the browser sets it with the correct boundary.

---

## Field Mapping (Frontend → Backend)

| Frontend Field | Backend Field |
|----------------|---------------|
| Full Name | `full_name` (or `first_name` + `last_name`) |
| Username | `username` |
| Email | `email` (read-only on update) |
| Phone | `phone` |
| Location | `location` |
| Bio | `bio` |
| LinkedIn | `linkedin_url` |
| Website | `website_url` |
| Profile Photo | `profile_photo` (file) |

---

## Profile Photo URL

After upload, the photo URL is in `user.profile_photo_url`:
```
http://localhost:8000/media/profile_photos/filename.jpg
```

Use this URL in an `<img src={user.profile_photo_url} />`.
