# Frontend — Next.js

The web pages of the project. They call the FastAPI backends, which run separately on their own ports.

| Page | Backend | Files |
|---|---|---|
| `/` | `crud_basics/main.py` · 8000 | `src/app/page.tsx` |
| `/products` | `crud_basics/product_db.py` · 8001 | `src/app/products/page.tsx` |
| `/catalog` | `appm2m` · 8002 | `src/app/catalog/` (page, ChatWidget, ImagePicker, CorsLab, DescribeStream) |
| `/graphql-shop` | `graphql_demo` · 8005 | `src/app/graphql-shop/page.tsx` |

Built with **Next.js 16 · React 19 · Tailwind CSS 4**. Colors and the theme (automatic dark mode) live in `src/app/globals.css`.

## Install and run

```powershell
npm install
npm run dev
```

Open **http://localhost:3000** (use `localhost`, not `127.0.0.1`, so the `/catalog` login cookie works).

The backend for each page must be running too — the easiest way is `uv run python run_all.py` from the project root.

## Other commands

```powershell
npm run build    # production build
npm run lint     # check the code
```
