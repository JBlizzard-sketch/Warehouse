import logging
import sqlite3
import os
import json
import subprocess
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from agents.agents import ScrapeAgent, ContentAgent, SocialAgent, WhatsAppAgent, ReviewAgent, MonitorAgent, LearningAgent, MultiPlatformAgent
from deploy import DeployManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(name)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "{{TELEGRAM_TOKEN}}")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "{{32_RANDOM_CHARS}}").encode()
SITE_URL = os.getenv("SITE_URL", "https://sasaparts.com/")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+254700123456")
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")
PROXY_LIST = os.getenv("PROXY_LIST", "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID", "{{GDRIVE_FOLDER_ID}}")
RENDER_API_KEY = os.getenv("RENDER_API_KEY", "{{RENDER_API_KEY}}")
RENDER_SERVICE_ID = os.getenv("RENDER_SERVICE_ID", "{{RENDER_SERVICE_ID}}")
FB_COOKIES_JSON = os.getenv("FB_COOKIES_JSON", "{}")
cipher = Fernet(ENCRYPTION_KEY)

DB_PATH = "./data/warehouse.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price TEXT, stock INTEGER);
CREATE TABLE IF NOT EXISTS fb_accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, cookies TEXT, status TEXT, score REAL);
CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, product_id INTEGER, receiver_details TEXT, status TEXT, tracking_id TEXT);
CREATE TABLE IF NOT EXISTS whatsapp_numbers (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, session_path TEXT, method TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, relevance_score REAL);
CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, status TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS cached_responses (id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT, response TEXT);
CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, review_text TEXT, rating INTEGER, source TEXT);
CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT, score REAL);
""")
conn.commit()

Load data from JSONs
def load_json(file):
try:
with open(file, "r") as f:
return json.load(f)
except Exception as e:
logger.error(f"JSON load error: {e}")
return {}

KEYWORDS = load_json("./data/keywords.json")
GROUPS = load_json("./data/groups.json")
SITES = load_json("./data/sites.json")
PROFILES = load_json("./data/profiles.json")
CONFIG = load_json("./data/config.json")
PROMPTS = load_json("./data/prompts.json")
BEHAVIORS = load_json("./data/behaviors.json")
AB_TEST = load_json("./data/ab_test.json")
ANOMALIES = load_json("./data/anomalies.json")
IOT_DEVICES = load_json("./data/iot_devices.json")
QUANTUM_KEYS = load_json("./data/quantum_keys.json")
VR_SIM = load_json("./data/vr_sim.json")
FEDERATED_MODELS = load_json("./data/federated_models.json")
VOICE_COMMANDS = load_json("./data/voice_commands.json")
FLUX_DNS = load_json("./data/flux_dns.json")
SELF_UPDATE = load_json("./data/self_update.json")
ETHICAL_CAPS = load_json("./data/ethical_caps.json")
REVIEWS = load_json("./data/reviews.json")
ORDERS = load_json("./data/orders.json")
CAPTCHAS = load_json("./data/captchas.json")

class Orchestrator:
def init(self):
self.whatsapp_process = None
self.scheduler = AsyncIOScheduler(timezone=timezone("Africa/Nairobi"))
self.scrape_agent = ScrapeAgent()
self.content_agent = ContentAgent()
self.social_agent = SocialAgent()
self.whatsapp_agent = WhatsAppAgent()
self.review_agent = ReviewAgent()
self.monitor_agent = MonitorAgent()
self.learning_agent = LearningAgent()
self.multiplatform_agent = MultiPlatformAgent()
self.deploy_manager = DeployManager()
self.scheduler.start()
self.config = CONFIG or {
"bots_to_create": 100, "posts_per_hour": 20, "post_hour_start": 6, "post_hour_end": 22,
"comments_per_post": 5, "groups_to_join": 10, "reviews_per_day": 50
}

def log_action(self, action, status, details=""):
    try:
        cursor.execute("INSERT INTO logs (action, status, details) VALUES (?, ?, ?)", 
                      (action, status, json.dumps(details)))
        conn.commit()
    except Exception as e:
        logger.error(f"Log error: {e}")

def save_number(self, number, session_path, method="baileys"):
    try:
        session_data = cipher.encrypt(b"{}").decode()
        cursor.execute("INSERT OR REPLACE INTO whatsapp_numbers (number, session_path, method, status) VALUES (?, ?, ?, ?)", 
                      (number, session_path, method, "pending"))
        conn.commit()
        self.log_action("whatsapp_save_number", "success", {"number": number})
    except Exception as e:
        self.log_action("whatsapp_save_number", "error", str(e))

def save_fb_account(self, username, cookies, score=0.5):
    try:
        encrypted_cookies = cipher.encrypt(json.dumps(cookies).encode()).decode()
        cursor.execute("INSERT OR REPLACE INTO fb_accounts (username, cookies, status, score) VALUES (?, ?, ?, ?)", 
                      (username, encrypted_cookies, "pending", score))
        conn.commit()
        self.log_action("fb_account_save", "success", {"username": username})
    except Exception as e:
        self.log_action("fb_account_save", "error", str(e))

async def start_whatsapp(self):
    if not self.whatsapp_process:
        self.whatsapp_process = subprocess.Popen(["node", "whatsapp_client.js"], stdout=open("./data/qr_log.txt", "w"))
        self.log_action("whatsapp_start", "started", "Baileys process initiated")

async def auto_create_accounts(self):
    try:
        num_bots = self.config["bots_to_create"]
        profiles = self.learning_agent.generate_profiles(num_bots)
        for profile in profiles:
            result = self.social_agent.create_account(profile["username"], profile["email"], profile["password"])
            if result["status"] == "captcha":
                await self.notify_admin_captcha(profile["username"], result["captcha_image"])
            score = self.learning_agent.score_bot({"engagement": 0, "ban_risk": 0, "uptime": 0})
            self.save_fb_account(profile["username"], result.get("cookies", {}), score)
        self.log_action("auto_create_account", "success", {"count": num_bots})
    except Exception as e:
        self.log_action("auto_create_account", "error", str(e))

async def auto_social_tasks(self):
    try:
        cursor.execute("SELECT id, score FROM fb_accounts WHERE status='active' ORDER BY score DESC LIMIT 20")
        bots = cursor.fetchall()
        groups = load_json("./data/groups.json")
        for bot_id, _ in bots[:self.config["groups_to_join"]]:
            for group in groups[:10]:
                self.social_agent.join_group(bot_id, group["id"])
                for _ in range(self.config["posts_per_hour"]):
                    post_result = self.social_agent.post(bot_id, group["id"])
                    if post_result["status"] == "captcha":
                        await self.notify_admin_captcha(bot_id, post_result["captcha_image"])
                    self.social_agent.scan_and_comment(bot_id, group["id"])
                self.multiplatform_agent.tweet(f"New auto spares! DM {WHATSAPP_NUMBER}")
                self.multiplatform_agent.post_instagram(f"Check out our spares! {SITE_URL}")
        self.log_action("auto_social_tasks", "success", {"bots": len(bots)})
    except Exception as e:
        self.log_action("auto_social_tasks", "error", str(e))

async def auto_generate_reviews(self):
    try:
        cursor.execute("SELECT id FROM products WHERE id NOT IN (SELECT product_id FROM reviews)")
        product_ids = [row[0] for row in cursor.fetchall()]
        for product_id in product_ids[:self.config["reviews_per_day"]]:
            result = self.review_agent.generate_review(product_id)
            self.log_action("auto_generate_review", result["status"], {"product_id": product_id})
    except Exception as e:
        self.log_action("auto_generate_review", "error", str(e))

async def auto_whatsapp_promos(self):
    try:
        cursor.execute("SELECT chat_id FROM orders WHERE status='pending'")
        chat_ids = [row[0] for row in cursor.fetchall()]
        for chat_id in chat_ids:
            cursor.execute("SELECT name FROM products WHERE id=(SELECT product_id FROM orders WHERE chat_id=?)", (chat_id,))
            product = cursor.fetchone()
            if product:
                message = f"Reminder: Your {product[0]} order is pending! DM {WHATSAPP_NUMBER} to confirm."
                self.whatsapp_agent.send_message(chat_id, message)
                self.whatsapp_agent.mock_phishing(chat_id)
    except Exception as e:
        self.log_action("auto_whatsapp_promos", "error", str(e))

async def notify_admin_captcha(self, bot_id, captcha_image):
    try:
        with open(f"./data/captcha_{bot_id}.png", "wb") as f:
            f.write(captcha_image)
        await Application.bot.send_photo(ADMIN_ID, photo=open(f"./data/captcha_{bot_id}.png", "rb"), 
                                        caption=f"CAPTCHA for bot {bot_id}. Reply with solution.")
    except Exception as e:
        self.log_action("captcha_notify", "error", str(e))

async def update_config(self, update: Update, param, value):
    try:
        self.config[param] = int(value)
        with open("./data/config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        self.log_action("update_config", "success", {"param": param, "value": value})
        await update.message.reply_text(f"Updated {param} to {value}")
    except Exception as e:
        self.log_action("update_config", "error", str(e))

async def run_follow_ups(self):
    try:
        cursor.execute("SELECT chat_id, product_id FROM orders WHERE status='pending' AND timestamp < ?", 
                      ((datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),))
        pending = cursor.fetchall()
        for chat_id, product_id in pending:
            cursor.execute("SELECT name, price FROM products WHERE id=?", (product_id,))
            product = cursor.fetchone()
            if product:
                name, price = product
                response = self.content_agent.query_product(f"Follow-up for {name}", chat_id)
                self.log_action("follow_up", "queued", {"chat_id": chat_id, "message": response.get("response", "")})
    except Exception as e:
        self.log_action("follow_ups", "error", str(e))

def schedule_tasks(self):
    self.scheduler.add_job(self.run_follow_ups, 'interval', hours=24)
    self.scheduler.add_job(self.scrape_agent.scrape_site, 'cron', hour=2)
    self.scheduler.add_job(self.monitor_agent.check_health, 'interval', minutes=30)
    self.scheduler.add_job(self.auto_create_accounts, 'interval', hours=24)
    self.scheduler.add_job(self.auto_social_tasks, 'interval', hours=12)
    self.scheduler.add_job(self.auto_generate_reviews, 'interval', hours=24)
    self.scheduler.add_job(self.auto_whatsapp_promos, 'interval', hours=24)
    self.scheduler.add_job(self.learning_agent.retrain_models, 'interval', hours=24)
  async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
keyboard = [
[InlineKeyboardButton("Setup", callback_data="setup"), InlineKeyboardButton("WhatsApp", callback_data="whatsapp_setup")],
[InlineKeyboardButton("Scrape", callback_data="scrape"), InlineKeyboardButton("Botnet", callback_data="botnet_status")],
[InlineKeyboardButton("DB Search", callback_data="db_search"), InlineKeyboardButton("Orders", callback_data="orders")],
[InlineKeyboardButton("Confirm Payment", callback_data="confirm_payment"), InlineKeyboardButton("Follow-ups", callback_data="follow_ups")],
[InlineKeyboardButton("Monitor", callback_data="monitor"), InlineKeyboardButton("Config", callback_data="config")],
[InlineKeyboardButton("Toggle Mode", callback_data="toggle_mode"), InlineKeyboardButton("Groq Suggest", callback_data="groq_suggest")]
]
reply_markup = InlineKeyboardMarkup(keyboard)
try:
cursor.execute("SELECT COUNT() FROM products")
product_count = cursor.fetchone()[0]
cursor.execute("SELECT id, username, score FROM fb_accounts WHERE status='active'")
bots = cursor.fetchall()
bot_count = len(bots)
cursor.execute("SELECT COUNT() FROM orders WHERE status='pending'")
order_count = cursor.fetchone()[0]
cursor.execute("SELECT id, name, relevance_score FROM groups")
groups = cursor.fetchall()
group_count = len(groups)
cursor.execute("SELECT COUNT(*) FROM reviews")
review_count = cursor.fetchone()[0]
bot_list = "\n".join([f"ID {b[0]}: {b[1]} (Score: {b[2]:.2f})" for b in bots[:5]]) or "No bots"
group_list = "\n".join([f"ID {g[0]}: {g[1]} (Score: {g[2]:.2f})" for g in groups[:5]]) or "No groups"
# Generate chart
plt.figure(figsize=(6, 4))
plt.bar(['Bots', 'Groups', 'Orders', 'Reviews'], [bot_count, group_count, order_count, review_count])
plt.savefig("./data/dashboard.png")
plt.close()
except Exception:
product_count = bot_count = order_count = group_count = review_count = 0
bot_list = group_list = "DB error"
mode = "Sandbox" if SANDBOX_MODE else "Live"
await update.message.reply_photo(
photo=open("./data/dashboard.png", "rb"),
caption=(
f"🏪 Auto Spares Dashboard ({mode})\n"
f"Products: {product_count}\nBots: {bot_count}\nGroups: {group_count}\nOrders: {order_count} pending\nReviews: {review_count}\n"
f"WhatsApp: {WHATSAPP_NUMBER} ({'active' if cursor.execute('SELECT status FROM whatsapp_numbers WHERE number=?', (WHATSAPP_NUMBER,)).fetchone() else 'pending'})\n"
f"Config: Bots/day: {orchestrator.config['bots_to_create']}, Posts/h: {orchestrator.config['posts_per_hour']}\n"
f"Bots (Top 5):\n{bot_list}\nGroups (Top 5):\n{group_list}"
),
parse_mode='Markdown', reply_markup=reply_markup
)

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
await update.message.reply_text("Paste keys (one per line): TELEGRAM_TOKEN, GROQ_API_KEY, SITE_URL, WHATSAPP_NUMBER, ENCRYPTION_KEY, FB_COOKIES_JSON, TWITTER_*, GITHUB_TOKEN")
context.user_data["setup_state"] = "awaiting_keys"

async def whatsapp_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
number = WHATSAPP_NUMBER
session_path = f"./data/whatsapp_session_{number}.json"
await orchestrator.start_whatsapp()
await update.message.reply_text(f"Scan QR from ./data/qr_{number}.txt for {number}. Reply 'done' when complete.")
context.user_data["whatsapp_state"] = {"number": number, "session_path": session_path}
orchestrator.save_number(number, session_path, orchestrator.whatsapp_agent.detect_best_method())

async def whatsapp_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if not context.args:
await update.message.reply_text("Usage: /whatsapp_add ")
return
number = context.args[0]
session_path = f"./data/whatsapp_session_{number}.json"
method = orchestrator.whatsapp_agent.detect_best_method()
subprocess.Popen(["node", "whatsapp_client.js", number], stdout=open(f"./data/qr_log_{number}.txt", "w")) if method == "baileys" else None
await update.message.reply_text(f"Scan QR from ./data/qr_{number}.txt for {number}. Reply 'done' when complete.")
context.user_data["whatsapp_state"] = {"number": number, "session_path": session_path}
orchestrator.save_number(number, session_path, method)

async def whatsapp_switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if not context.args:
await update.message.reply_text("Usage: /whatsapp_switch <number_id>")
return
number_id = context.args[0]
cursor.execute("SELECT number, session_path, method FROM whatsapp_numbers WHERE id=?", (number_id,))
result = cursor.fetchone()
if result:
number, session_path, method = result
cursor.execute("UPDATE whatsapp_numbers SET status='active' WHERE id=?", (number_id,))
cursor.execute("UPDATE whatsapp_numbers SET status='inactive' WHERE id!=?", (number_id,))
conn.commit()
await update.message.reply_text(f"Switched to {number} ({method}).")
orchestrator.log_action("whatsapp_switch", "success", {"number": number})
else:
await update.message.reply_text("Number ID not found.")

async def botnet_create_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if len(context.args) < 3:
await update.message.reply_text("Usage: /botnet_create_account ")
return
username, email, password = context.args[0], context.args[1], context.args[2]
result = orchestrator.social_agent.create_account(username, email, password)
if result["status"] == "captcha":
await orchestrator.notify_admin_captcha(username, result["captcha_image"])
await update.message.reply_text(f"Create account: {result['status']}" + (f", error: {result['error']}" if result['status'] == "error" else ""))

async def botnet_search_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if not context.args:
await update.message.reply_text("Usage: /botnet_search_groups <account_id>")
return
account_id = context.args[0]
result = orchestrator.social_agent.search_groups(account_id)
if result["status"] == "success":
groups = "\n".join([f"{g['name']} (Score: {g['relevance_score']:.2f})" for g in result["groups"]])
await update.message.reply_text(f"Found groups:\n{groups}")
else:
await update.message.reply_text(f"Error: {result['error']}")

async def botnet_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if len(context.args) < 2:
await update.message.reply_text("Usage: /botnet_join_group <account_id> <group_id>")
return
account_id, group_id = context.args[0], context.args[1]
result = orchestrator.social_agent.join_group(account_id, group_id)
await update.message.reply_text(f"Join group: {result['status']}" + (f", error: {result['error']}" if result['status'] == "error" else ""))

async def botnet_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if len(context.args) < 2:
await update.message.reply_text("Usage: /botnet_post <account_id> <group_id>")
return
account_id, group_id = context.args[0], context.args[1]
result = orchestrator.social_agent.post(account_id, group_id)
if result["status"] == "captcha":
await orchestrator.notify_admin_captcha(account_id, result["captcha_image"])
await update.message.reply_text(f"Post: {result['status']}" + (f", content: {result['content']}" if result['status'] == "success" else f", error: {result['error']}"))

async def botnet_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if len(context.args) < 3:
await update.message.reply_text("Usage: /botnet_comment <account_id> <group_id> ")
return
account_id, group_id, query = context.args[0], context.args[1], " ".join(context.args[2:])
result = orchestrator.social_agent.comment(account_id, group_id, query)
if result["status"] == "captcha":
await orchestrator.notify_admin_captcha(account_id, result["captcha_image"])
await update.message.reply_text(f"Comment: {result['status']}" + (f", query: {result['query']}" if result['status'] == "success" else f", error: {result['error']}"))

async def botnet_like_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if len(context.args) < 2:
await update.message.reply_text("Usage: /botnet_like_share <account_id> <group_id>")
return
account_id, group_id = context.args[0], context.args[1]
result = orchestrator.social_agent.like_share(account_id, group_id)
await update.message.reply_text(f"Like/Share: {result['status']}" + (f", error: {result['error']}" if result['status'] == "error" else ""))

async def botnet_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
cursor.execute("SELECT id, username, status, score FROM fb_accounts")
accounts = cursor.fetchall()
status = "\n".join([f"ID {a[0]}: {a[1]} ({a[2]}, Score: {a[3]:.2f})" for a in accounts[:10]]) or "No accounts"
await update.message.reply_text(f"FB Bots:\n{status}")

async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
url = context.args[0] if context.args else SITE_URL
keyboard = [[InlineKeyboardButton("Confirm", callback_data=f"scrape_confirm_{url}"),
InlineKeyboardButton("Cancel", callback_data="scrape_cancel")]]
await update.message.reply_text(f"Scrape {url}?", reply_markup=InlineKeyboardMarkup(keyboard))

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
return await update.message.reply_text("Usage: /confirm_payment <chat_id>")
chat_id = context.args[0]
cursor.execute("SELECT product_id FROM orders WHERE chat_id=?", (chat_id,))
order = cursor.fetchone()
if order:
product_id = order[0]
cursor.execute("SELECT name, price FROM products WHERE id=?", (product_id,))
product = cursor.fetchone()
tracking_id = f"G4S-KEN-{os.urandom(3).hex()}"
cursor.execute("UPDATE orders SET status='confirmed', tracking_id=? WHERE chat_id=?",
(tracking_id, chat_id))
conn.commit()
name, price = product if product else ("Unknown", "Unknown")
await update.message.reply_text(f"Payment confirmed for {chat_id}. {name} (KES {price}) shipping via {tracking_id}, G4S 1-2 days.")
orchestrator.log_action("confirm_payment", "success", {"chat_id": chat_id})
orchestrator.whatsapp_agent.send_message(chat_id, f"Your order for {name} is confirmed! Tracking: {tracking_id}")
else:
await update.message.reply_text("Order not found.")

async def follow_ups(update: Update, context: ContextTypes.DEFAULT_TYPE):
await orchestrator.run_follow_ups()
await update.message.reply_text("Follow-ups queued for pending orders.")

async def db_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text("Usage: /db_search table:products|fb_accounts|orders|groups|reviews")
return
query, table = context.args[0], context.args[1] if len(context.args) > 1 else "products"
if table not in ["products", "fb_accounts", "orders", "whatsapp_numbers", "groups", "reviews"]:
await update.message.reply_text("Table must be products, fb_accounts, orders, whatsapp_numbers, groups, reviews")
return
cursor.execute(f"SELECT * FROM {table} WHERE name LIKE ? OR chat_id LIKE ? OR url LIKE ? OR review_text LIKE ?",
(f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
results = cursor.fetchall()
response = "\n".join([str(r) for r in results]) or "No results"
await update.message.reply_text(f"Search {table}:\n{response}")

async def db_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text("Usage: /db_filter

<field=value>")
return
table, condition = context.args[0], context.args[1]
field, value = condition.split("=")
if table not in ["products", "fb_accounts", "orders", "whatsapp_numbers", "groups", "reviews"]:
await update.message.reply_text("Table must be products, fb_accounts, orders, whatsapp_numbers, groups, reviews")
return
cursor.execute(f"SELECT * FROM {table} WHERE {field}=?", (value,))
results = cursor.fetchall()
response = "\n".join([str(r) for r in results]) or "No results"
await update.message.reply_text(f"Filter {table} {field}={value}:\n{response}")
async def db_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if not context.args:
await update.message.reply_text("Usage: /db_add

<json_data>")
return
table, data = context.args[0], " ".join(context.args[1:])
try:
data_json = json.loads(data)
if table == "products":
cursor.execute("INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
(data_json.get("name"), data_json.get("description"), data_json.get("price"), data_json.get("stock")))
elif table == "fb_accounts":
orchestrator.save_fb_account(data_json.get("username"), data_json.get("cookies"))
elif table == "orders":
receiver_details = json.dumps(data_json.get("receiver_details", {}))
cursor.execute("INSERT INTO orders (chat_id, product_id, receiver_details, status) VALUES (?, ?, ?, ?)",
(data_json.get("chat_id"), data_json.get("product_id"), receiver_details, "pending"))
elif table == "groups":
cursor.execute("INSERT INTO groups (name, url, relevance_score) VALUES (?, ?, ?)",
(data_json.get("name"), data_json.get("url"), data_json.get("relevance_score", 0.5)))
elif table == "reviews":
cursor.execute("INSERT INTO reviews (product_id, review_text, rating, source) VALUES (?, ?, ?, ?)",
(data_json.get("product_id"), data_json.get("review_text"), data_json.get("rating"), data_json.get("source", "telegram")))
elif table == "batch":
for item in data_json:
if item.get("table") == "products":
cursor.execute("INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
(item.get("name"), item.get("description"), item.get("price"), item.get("stock")))
elif item.get("table") == "orders":
receiver_details = json.dumps(item.get("receiver_details", {}))
cursor.execute("INSERT INTO orders (chat_id, product_id, receiver_details, status) VALUES (?, ?, ?, ?)",
(item.get("chat_id"), item.get("product_id"), receiver_details, "pending"))
conn.commit()
await update.message.reply_text(f"Added to {table}")
except Exception as e:
await update.message.reply_text(f"Error: {e}")
orchestrator.log_action("db_add", "error", str(e))
async def db_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if not context.args:
await update.message.reply_text("Usage: /db_delete

")
return
table, id_ = context.args[0], context.args[1]
if table not in ["products", "fb_accounts", "orders", "whatsapp_numbers", "groups", "reviews"]:
await update.message.reply_text("Table must be products, fb_accounts, orders, whatsapp_numbers, groups, reviews")
return
cursor.execute(f"DELETE FROM {table} WHERE id=?", (id_,))
conn.commit()
await update.message.reply_text(f"Deleted ID {id_} from {table}")
async def edit_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
if not context.args:
await update.message.reply_text("Usage: /edit_json ")
return
file, key, value = context.args[0], context.args[1], " ".join(context.args[2:])
try:
json_file = f"./data/{file}.json"
data = load_json(json_file)
if file == "keywords":
data.append({"keyword": key, "score": float(value)})
elif file == "groups":
data.append({"id": len(data) + 1, "name": key, "url": value, "relevance_score": 0.5})
elif file == "sites":
data.append(value)
elif file == "config":
data[key] = int(value)
elif file == "profiles":
data.append({"username": key, "email": value, "password": os.urandom(8).hex()})
with open(json_file, "w") as f:
json.dump(data, f, indent=2)
await update.message.reply_text(f"Updated {file}.json")
orchestrator.log_action("edit_json", "success", {"file": file, "key": key, "value": value})
except Exception as e:
await update.message.reply_text(f"Error: {e}")
orchestrator.log_action("edit_json", "error", str(e))

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
if str(update.message.from_user.id) != ADMIN_ID:
await update.message.reply_text("Admin only!")
return
result = orchestrator.monitor_agent.check_health()
await update.message.reply_text(f"Health: {result['status']}\nDetails: {result['details']}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data = query.data
if data.startswith("scrape_confirm_"):
url = data.replace("scrape_confirm_", "")
result = orchestrator.scrape_agent.scrape_site(url)
await query.message.reply_text(f"Scrape {url}: {result['status']}, {result.get('products', 0)} products added.")
orchestrator.log_action("scrape", result["status"], {"url": url})
elif data == "scrape_cancel":
await query.message.reply_text("Scrape cancelled.")
elif data == "setup":
await setup(query, context)
elif data == "whatsapp_setup":
await whatsapp_setup(query, context)
elif data == "botnet_status":
await botnet_status(query, context)
elif data == "db_search":
await query.message.reply_text("Use /db_search

")
elif data == "orders":
cursor.execute("SELECT chat_id, product_id, status FROM orders")
orders = cursor.fetchall()
response = "\n".join([f"Chat {o[0]}: Product {o[1]} ({o[2]})" for o in orders]) or "No orders"
await query.message.reply_text(f"Orders:\n{response}")
elif data == "confirm_payment":
await query.message.reply_text("Use /confirm_payment <chat_id>")
elif data == "follow_ups":
await follow_ups(query, context)
elif data == "monitor":
await monitor(query, context)
elif data == "config":
keyboard = [
[InlineKeyboardButton(f"Bots/day: {orchestrator.config['bots_to_create']}", callback_data="config_bots")],
[InlineKeyboardButton(f"Posts/h: {orchestrator.config['posts_per_hour']}", callback_data="config_posts")],
[InlineKeyboardButton(f"Start Hour: {orchestrator.config['post_hour_start']}", callback_data="config_start_hour")],
[InlineKeyboardButton(f"End Hour: {orchestrator.config['post_hour_end']}", callback_data="config_end_hour")],
[InlineKeyboardButton(f"Comments/Post: {orchestrator.config['comments_per_post']}", callback_data="config_comments")],
[InlineKeyboardButton(f"Groups/Join: {orchestrator.config['groups_to_join']}", callback_data="config_groups")],
[InlineKeyboardButton(f"Reviews/Day: {orchestrator.config['reviews_per_day']}", callback_data="config_reviews")]
]
await query.message.reply_text("Adjust config:", reply_markup=InlineKeyboardMarkup(keyboard))
elif data.startswith("config_"):
param = data.replace("config_", "")
context.user_data["config_param"] = param
await query.message.reply_text(f"Enter value for {param} (e.g., 1-100 for bots, 6-22 for hours)")
elif data == "toggle_mode":
global SANDBOX_MODE
SANDBOX_MODE = not SANDBOX_MODE
await query.message.reply_text(f"Mode switched to {'Sandbox' if SANDBOX_MODE else 'Live'}")
orchestrator.log_action("toggle_mode", "success", {"mode": "Sandbox" if SANDBOX_MODE else "Live"})
elif data == "groq_suggest":
suggestion = orchestrator.content_agent.groq_suggest()
keyboard = [[InlineKeyboardButton("Implement", callback_data=f"implement_suggestion_{suggestion['action']}")]]
await query.message.reply_text(f"Groq Suggestion: {suggestion['text']}", reply_markup=InlineKeyboardMarkup(keyboard))
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text
if context.user_data.get("whatsapp_state") and text.lower() == "done":
number = context.user_data["whatsapp_state"]["number"]
cursor.execute("UPDATE whatsapp_numbers SET status='active' WHERE number=?", (number,))
conn.commit()
await update.message.reply_text(f"WhatsApp {number} active!")
orchestrator.log_action("whatsapp_auth", "success", {"number": number})
context.user_data.pop("whatsapp_state")
elif context.user_data.get("setup_state") == "awaiting_keys":
keys = text.split("\n")
if len(keys) >= 10:
with open(".env", "w") as f:
f.write(f"TELEGRAM_TOKEN={keys[0]}\nGROQ_API_KEY={keys[1]}\nSITE_URL={keys[2]}\nWHATSAPP_NUMBER={keys[3]}\nENCRYPTION_KEY={keys[4]}\nFB_COOKIES_JSON={keys[5]}\nTWITTER_API_KEY={keys[6]}\nTWITTER_API_SECRET={keys[7]}\nTWITTER_ACCESS_TOKEN={keys[8]}\nTWITTER_ACCESS_TOKEN_SECRET={keys[9]}\n")
await update.message.reply_text("Keys saved! Bot restarting...")
context.user_data.pop("setup_state")
else:
await update.message.reply_text("Need 10 keys: TELEGRAM_TOKEN, GROQ_API_KEY, SITE_URL, WHATSAPP_NUMBER, ENCRYPTION_KEY, FB_COOKIES_JSON, TWITTER_*")
elif context.user_data.get("config_param"):
param = context.user_data["config_param"]
await orchestrator.update_config(update, param, text)
context.user_data.pop("config_param")
elif text.lower().startswith("query:"):
query = text[6:].strip()
result = orchestrator.content_agent.query_product(query, str(update.message.chat_id))
await update.message.reply_text(result.get("response", f"Error: {result.get('error', 'Unknown')}"))
if result["status"] == "success" and result.get("product"):
orchestrator.whatsapp_agent.send_message(str(update.message.chat_id), result["response"])
elif update.message.voice:
# Voice command stub
await update.message.reply_text("Voice commands: 'Create 50 bots' → /botnet_create_account batch 50")
elif text.lower() == "edit_json":
await edit_json(update, context)

def main():
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setup", setup))
app.add_handler(CommandHandler("whatsapp_setup", whatsapp_setup))
app.add_handler(CommandHandler("whatsapp_add", whatsapp_add))
app.add_handler(CommandHandler("whatsapp_switch", whatsapp_switch))
app.add_handler(CommandHandler("botnet_create_account", botnet_create_account))
app.add_handler(CommandHandler("botnet_search_groups", botnet_search_groups))
app.add_handler(CommandHandler("botnet_join_group", botnet_join_group))
app.add_handler(CommandHandler("botnet_post", botnet_post))
app.add_handler(CommandHandler("botnet_comment", botnet_comment))
app.add_handler(CommandHandler("botnet_like_share", botnet_like_share))
app.add_handler(CommandHandler("botnet_status", botnet_status))
app.add_handler(CommandHandler("scrape", scrape))
app.add_handler(CommandHandler("confirm_payment", confirm_payment))
app.add_handler(CommandHandler("follow_ups", follow_ups))
app.add_handler(CommandHandler("db_search", db_search))
app.add_handler(CommandHandler("db_filter", db_filter))
app.add_handler(CommandHandler("db_add", db_add))
app.add_handler(CommandHandler("db_delete", db_delete))
app.add_handler(CommandHandler("edit_json", edit_json))
app.add_handler(CommandHandler("monitor", monitor))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.VOICE, message_handler))
orchestrator.schedule_tasks()
app.run_polling()

if name == "main":
main()

