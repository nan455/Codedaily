"""
test_email.py — Test email sending from your local machine or Render shell.

LOCAL:  python test_email.py
RENDER: Open Render dashboard → your service → Shell tab → python test_email.py
"""
import os, sys
from app import app, mail, _send_daily_emails, Subscriber, APP_URL
from flask_mail import Message

def test_smtp(to_email=None):
    """Send a single raw SMTP test email — fastest way to verify credentials."""
    with app.app_context():
        to = to_email or os.environ.get("GMAIL_USER", "")
        if not to:
            print("❌ No email address. Pass one as argument: python test_email.py you@gmail.com")
            return False
        
        print(f"\n{'='*50}")
        print("SMTP CONFIG CHECK")
        print(f"{'='*50}")
        print(f"GMAIL_USER:        {os.environ.get('GMAIL_USER', '❌ NOT SET')}")
        print(f"GMAIL_APP_PASSWORD: {'✅ SET (' + str(len(os.environ.get('GMAIL_APP_PASSWORD',''))) + ' chars)' if os.environ.get('GMAIL_APP_PASSWORD') else '❌ NOT SET'}")
        print(f"APP_URL:           {APP_URL}")
        print(f"Sending test to:   {to}")
        print(f"{'='*50}\n")
        
        try:
            mail.send(Message(
                subject="✅ CodeDaily SMTP Test — It works!",
                recipients=[to],
                html=f"""
                <h2>✅ SMTP is working correctly!</h2>
                <p><strong>GMAIL_USER:</strong> {os.environ.get('GMAIL_USER')}</p>
                <p><strong>APP_URL:</strong> {APP_URL}</p>
                <p><strong>Dashboard link test:</strong> <a href="{APP_URL}/dashboard">{APP_URL}/dashboard</a></p>
                <p>If you see this email, your email config on Render is correct.</p>
                """
            ))
            print(f"✅ SUCCESS! Test email sent to {to}")
            print("   Check your inbox (and spam folder).\n")
            return True
        except Exception as e:
            print(f"❌ FAILED: {e}")
            print("\nCommon fixes:")
            print("  1. Make sure GMAIL_USER and GMAIL_APP_PASSWORD are set in Render env vars")
            print("  2. The app password must be 16 chars with NO spaces")
            print("  3. Gmail 2FA must be ON for app passwords to work")
            print("  4. Try generating a fresh app password at myaccount.google.com\n")
            return False

def test_daily_emails():
    """Trigger the exact same function the 8 AM cron job calls."""
    with app.app_context():
        print("\n🔍 Fetching active subscribers...")
        subs = Subscriber.query.filter_by(active=True).all()
        print(f"📋 Found {len(subs)} active subscriber(s).")
        
        if not subs:
            print("⚠️  No subscribers. Go subscribe on your site first!\n")
            return
        
        print("🚀 Sending daily emails now...\n")
        try:
            _send_daily_emails()
            print("✅ Done! Check inboxes and Render logs.\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    email_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Step 1: Test raw SMTP first
    smtp_ok = test_smtp(email_arg)
    
    # Step 2: If SMTP works, test daily send
    if smtp_ok:
        print("\nNow testing the full daily email flow...\n")
        test_daily_emails()