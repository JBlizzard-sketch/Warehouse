import requests
import os
from dotenv import load_dotenv

load_dotenv()
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
RENDER_SERVICE_ID = os.getenv("RENDER_SERVICE_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def deploy():
try:
headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}
response = requests.post(f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys", headers=headers)
if response.status_code == 200:
print("Deploy triggered")
# Self-update via GitHub
update_response = requests.get("https://api.github.com/repos/owner/repo/contents/auto_spares_bot.py",
headers={"Authorization": f"token {GITHUB_TOKEN}"})
if update_response.status_code == 200:
print("Code updated")
except Exception as e:
print(f"Deploy error: {e}")

if name == "main":
deploy()
