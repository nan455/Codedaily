import os
from app import app, start_scheduler

# Only start the scheduler in the MAIN gunicorn worker (not in every worker)
# Render free tier uses 1 worker, so this is fine.
# If you ever upgrade to multiple workers, use a Redis-based scheduler instead.
if os.environ.get("DYNO") or os.environ.get("RENDER"):
    # We're on Render — start scheduler
    start_scheduler()
else:
    # Local dev — start scheduler too
    start_scheduler()

if __name__ == "__main__":
    app.run()