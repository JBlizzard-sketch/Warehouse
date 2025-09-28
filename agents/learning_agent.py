import xgboost as xgb
from groq import Groq
import numpy as np
import json
from .content_agent import GroqClient

class LearningAgent:
def init(self):
self.groq_client = GroqClient()
self.model = xgb.XGBClassifier()
self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_profiles(self, num_profiles):
    try:
        prompt = f"Generate {num_profiles} realistic Kenyan usernames, emails, passwords, bios for auto spares bots."
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        ).choices[0].message.content
        profiles = json.loads(response)
        with open("./data/profiles.json", "w") as f:
            json.dump(profiles, f)
        return profiles
    except Exception as e:
        return [{"username": f"User_{i}", "email": f"user{i}@example.com", "password": f"Pass{i}!"} for i in range(num_profiles)]

def score_bot(self, features):
    try:
        X = np.array([[features["engagement"], features["ban_risk"], features["uptime"]]])
        return self.model.predict_proba(X)[0][1]
    except Exception as e:
        return 0.5

def retrain_models(self):
    try:
        cursor.execute("SELECT details FROM logs WHERE action IN ('post', 'comment', 'like_share') AND timestamp > ?",
                      ((datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),))
        logs = [json.loads(row[0]) for row in cursor.fetchall()]
        X, y = [], []
        for log in logs:
            X.append([log.get("engagement", 0), log.get("ban_risk", 0), log.get("uptime", 0)])
            y.append(1 if log.get("status") == "success" else 0)
        if X and y:
            self.model.fit(np.array(X), np.array(y))
            with open("./data/federated_models.json", "w") as f:
                json.dump(self.model.get_params(), f)
            prompt = f"Model retrained with {len(X)} samples. Suggest adjustments?"
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768", messages=[{"role": "user", "content": prompt}], max_tokens=200
            ).choices[0].message.content
            Application.bot.send_message(ADMIN_ID, f"Model Update: {response}")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
