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
    request_start = time.perf_counter()
    wall_start = time.time()
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

    db_start = time.perf_counter() # Start db time measure
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
    db_time = time.perf_counter() - db_start  # End service time measure

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

    total_request_time = time.perf_counter() - request_start
    server_time = total_request_time - db_time

    wall_response_time = time.time() - wall_start

    logging.info(f"[DB TIME] {db_time:.10f}s")
    logging.info(f"[SERVER TIME] {server_time:.10f}s")
    logging.info(f"[TOTAL SERVICE TIME] {total_request_time:.10f}s")
    logging.info(f"[RESPONSE TIME] {wall_response_time:.10f}s")
    
    logging.info(f"[RENDER TIME] {render_time:.10f}s")

    # Track and log total service time and its average
    # if not hasattr(request.app.state, "server_service_times"):
    #     request.app.state.server_service_times = []
    # request.app.state.server_service_times.append(total_request_time)
    # avg_total_service_time = sum(request.app.state.server_service_times) / len(request.app.state.server_service_times)
    # logging.info(f"[TOTAL SERVICE TIME] {total_request_time:.10f}s | [AVG TOTAL SERVICE TIME] {avg_total_service_time:.10f}s")

    return response

@app.middleware("http")
async def full_service_timer(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    request.state.total_request_time = duration
    logging.info(f"[TOTAL REQUEST TIME] {duration:.10f}s")
    return response