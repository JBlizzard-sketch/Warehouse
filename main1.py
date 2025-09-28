import os
import subprocess
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from bot.bot import Orchestrator
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

app = Flask(name)

@app.route('/whatsapp_message', methods=['POST'])
def whatsapp_message():
data = request.json
number = data.get('number')
chat_id = data.get('chat_id')
message = data.get('message')
result = orchestrator.whatsapp_agent.handle_message({"message": {"conversation": message}}, number, chat_id)
return jsonify(result)

def start_node():
try:
process = subprocess.Popen(["node", "whatsapp_client.js"], stdout=open("./data/qr_log.txt", "w"))
logger.info("Node started")
return process
except Exception as e:
logger.error(f"Node error: {e}")
return None

def main():
global orchestrator
orchestrator = Orchestrator()
scheduler = BackgroundScheduler(timezone=timezone("Africa/Nairobi"))
node_process = start_node()
scheduler.add_job(orchestrator.run_follow_ups, 'interval', hours=24)
scheduler.add_job(orchestrator.scrape_agent.scrape_site, 'cron', hour=2)
scheduler.add_job(orchestrator.monitor_agent.check_health, 'interval', minutes=30)
scheduler.add_job(orchestrator.auto_create_accounts, 'interval', hours=24)
scheduler.add_job(orchestrator.auto_social_tasks, 'interval', hours=12)
scheduler.add_job(orchestrator.auto_generate_reviews, 'interval', hours=24)
scheduler.add_job(orchestrator.auto_whatsapp_promos, 'interval', hours=24)
scheduler.add_job(orchestrator.learning_agent.retrain_models, 'interval', hours=24)
scheduler.start()
from threading import Thread
flask_thread = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000})
flask_thread.start()
orchestrator.main()

if name == "main":
main()
