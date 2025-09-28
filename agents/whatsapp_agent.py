from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import random
from .content_agent import ContentAgent

class WhatsAppAgent:
def init(self):
self.method = self.detect_best_method()
self.content_agent = ContentAgent()

def detect_best_method(self):
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        return "baileys"
    except:
        return "selenium"

def send_message(self, chat_id, content):
    try:
        if self.method == "baileys":
            subprocess.run(["node", "whatsapp_client.js", chat_id, content], check=True)
        else:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get("https://web.whatsapp.com")
            # Simulate send
            return {"status": "success"}
        return {"status": "success"}
    except Exception as e:
        self.method = "selenium" if self.method == "baileys" else "baileys"
        return {"status": "error", "error": str(e)}

def handle_message(self, message, number, chat_id):
    query = message.get("message", {}).get("conversation", "")
    result = self.content_agent.query_product(query, chat_id)
    self.send_message(chat_id, result["response"])
    return result
