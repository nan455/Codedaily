from app import app, db, _send_daily_emails, Subscriber

def run_email_test():
    with app.app_context():
        print("🔍 Fetching active subscribers from the database...")
        subs = Subscriber.query.filter_by(active=True).all()
        print(f"📋 Found {len(subs)} active subscribers.")

        if len(subs) == 0:
            print("⚠️ No active subscribers found. Go to your website and subscribe first!")
            return

        print("🚀 Triggering daily emails...")
        try:
            # This calls the exact function your 8 AM cron job uses
            _send_daily_emails()
            print("✅ Emails sent successfully! Check your inbox.")
        except Exception as e:
            print(f"❌ Error sending emails: {e}")

if __name__ == "__main__":
    run_email_test()