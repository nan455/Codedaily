from app import app, Subscriber
import cloudscraper

def test_lc_submit(user_email):
    with app.app_context():
        print(f"🔍 Looking up user {user_email}...")
        sub = Subscriber.query.filter_by(email=user_email).first()
        
        if not sub:
            print("❌ User not found in database.")
            return
        if not sub.lc_session:
            print("❌ User found, but no LEETCODE_SESSION cookie is saved for them.")
            return

        print(f"🔗 Simulating submission for LeetCode user: {sub.lc_username}")
        
        # We'll submit a blank/dummy Python solution to Two Sum (Slug: two-sum, ID: 1)
        slug = "two-sum"
        question_id = "1"
        dummy_code = "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass"
        
        scraper = cloudscraper.create_scraper()
        scraper.cookies.set("LEETCODE_SESSION", sub.lc_session, domain="leetcode.com")

        try:
            print("🛡️  Fetching CSRF token...")
            scraper.get("https://leetcode.com/", timeout=10)
            csrf_token = scraper.cookies.get("csrftoken", "")

            print("🚀 Pushing code to LeetCode servers...")
            resp = scraper.post(
                f"https://leetcode.com/problems/{slug}/submit/",
                json={"lang": "python3", "question_id": question_id, "typed_code": dummy_code},
                headers={
                    "Content-Type": "application/json",
                    "Referer": f"https://leetcode.com/problems/{slug}/",
                    "X-CSRFToken": csrf_token,
                },
                timeout=15,
            )

            if resp.status_code == 200:
                result = resp.json()
                sid = result.get("submission_id")
                if sid:
                    print(f"✅ Success! Submission accepted by LeetCode.")
                    print(f"👁️  View it here: https://leetcode.com/submissions/detail/{sid}/")
                else:
                    print("⚠️ Submitted, but LeetCode didn't return a Submission ID. Raw response:")
                    print(result)
            elif resp.status_code == 403:
                print("❌ 403 Forbidden: Your session cookie has expired OR Cloudflare blocked the request.")
            else:
                print(f"❌ Failed with status code {resp.status_code}: {resp.text}")

        except Exception as e:
            print(f"❌ Fatal Error: {e}")

if __name__ == "__main__":
    # REPLACE THIS with the email you used to subscribe to your app
    YOUR_EMAIL = "your.email@gmail.com" 
    test_lc_submit(YOUR_EMAIL)