# Cookie — Remember the User

Class example: let the server "remember" a user even though HTTP is stateless, by using a cookie.

| Endpoint | What it does |
|---|---|
| `POST /set-name` | Takes a name → creates a random `session_id` → stores `session_id → name` on the server → sends a cookie (HttpOnly, 1 hour) |
| `GET /welcome` | Reads the cookie → greets the user by name · no cookie = **401** |
| `POST /forget` | Deletes the server-side session + tells the browser to delete the cookie |

## What I learned

- **`response.set_cookie(...)`** — tells the browser to store a cookie (sent in the `Set-Cookie` header)
- **`Cookie()`** — reads the cookie the browser sends automatically with every request
- **`response.delete_cookie(...)`** — logout
- **Store only a random session ID** (`secrets.token_urlsafe`), never the name or user ID itself
- **`httponly=True`** — JavaScript can't read the cookie (protects against XSS)
- Bugs I hit: `sessions = dict[str, str] = {}` needs `:` · `http_only` must be `httponly`

Full version in the main project (sessions in Redis + Remember me): [`appm2m/COOKIE.md`](../appm2m/COOKIE.md)

## Run

```powershell
cd cookie
uv run fastapi dev main.py --port 8010
```

Open `http://127.0.0.1:8010/docs` → `POST /set-name` → `GET /welcome`
