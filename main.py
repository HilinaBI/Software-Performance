from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import time
import logging

logging.basicConfig(
    filename="service_time.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple in-memory cache: {query: (results, timestamp)}
cache = {}
CACHE_TTL = 300  # 5 minutes

service_times = []

def get_columns():
    """Return list of columns in movies table"""
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(movies)")
        columns = [row[1] for row in cursor.fetchall()]
    return columns

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
def search_movie(request: Request, title: str = ""):
    start_time = time.time()

    # Check cache first
    now = time.time()
    if title in cache:
        results, cached_time = cache[title]
        if now - cached_time < CACHE_TTL:
            print(f"[CACHE HIT] '{title}' served in {time.time() - start_time:.4f}s")
            return templates.TemplateResponse("search.html", {
                "request": request,
                "results": results,
                "query": title
            })

    # Prepare SQL columns to select based on DB schema
    columns = ["primaryTitle", "startYear", "averageRating", "numVotes", "runtimeMinutes", "genres", "actors", "directors"]
    db_columns = get_columns()
    if "writers" in db_columns:
        columns.append("writers")

    columns_sql = ", ".join(columns)

    service_start = time.perf_counter() # Start service time measure
    # Query the database and convert results to dicts for key access in template
    with sqlite3.connect("movies.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {columns_sql}
            FROM movies
            WHERE lower(primaryTitle) LIKE ?
            LIMIT 10
        """, ('%' + title.lower() + '%',))
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]  # <-- convert to dicts
    service_time = time.perf_counter() - service_start  # End service time measure
    # Aggregation of service time
    service_times.append(service_time)  
    avg_service_time = sum(service_times) / len(service_times)
    logging.info(f"[SERVICE TIME] {service_time:.10f}s | [AVG SERVICE TIME] {avg_service_time:.10f}s")

    # Cache results
    cache[title] = (results, now)

    print(f"[CACHE MISS] '{title}' took {time.time() - start_time:.4f}s")

    render_start = time.perf_counter()
    response = templates.TemplateResponse("search.html", {
        "request": request,
        "results": results,
        "query": title
    })
    render_time = time.perf_counter() - render_start
    logging.info(f"[RENDER TIME] {render_time:.10f}s")
    return response

@app.middleware("http")
async def full_service_timer(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    logging.info(f"[TOTAL REQUEST TIME] {duration:.10f}s")
    return response