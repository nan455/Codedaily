from app import app, start_scheduler

# Start the APScheduler (daily email cron) when gunicorn boots
start_scheduler()

if __name__ == "__main__":
    app.run()
