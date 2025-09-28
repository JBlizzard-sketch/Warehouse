from groq import Groq
import json
from .scrape_agent import ScrapeAgent # Import shared scrape agent

class GroqClient:
def init(self):
self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def score_keyword(self, text):
    try:
        prompt = f"Score relevance of '{text}' to auto spares (0-1)."
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        ).choices[0].message.content
        return float(response)
    except Exception as e:
        return 0.5
class ContentAgent:
def init(self):
self.groq_client = GroqClient()
self.scrape_agent = ScrapeAgent()
self.prompt_templates = json.load(open("./data/prompts.json"))
self.behaviors = json.load(open("./data/behaviors.json"))

def query_product(self, query, chat_id):
    try:
        tone = self.detect_tone(query)
        priority = self.prioritize_query(query)
        product = self.scrape_agent.get_product_match(query)
        prompt = self.prompt_templates["response"].format(tone=tone, query=query, product=product, number=WHATSAPP_NUMBER)
        response = self.groq_client.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        ).choices[0].message.content
        cursor.execute("INSERT OR REPLACE INTO cached_responses (query, response) VALUES (?, ?)", 
                      (query, response))
        conn.commit()
        if product:
            cursor.execute("INSERT INTO orders (chat_id, product_id, status) VALUES (?, ?, ?)",
                          (chat_id, product["id"], "pending"))
            conn.commit()
        self.log_action("query_product", "success", {"query": query, "response": response})
        return {"status": "success", "response": response}
    except Exception as e:
        self.log_action("query_product", "error", str(e))
        return {"status": "error", "error": str(e)}

def detect_tone(self, query):
    # Implementation as before, but with behaviors.json for personas
    behaviors = self.behaviors["tones"]
    for tone in behaviors:
        if any(word in query.lower() for word in tone["keywords"]):
            return tone["name"]
    return "english"

def prioritize_query(self, query):
    urgency_words = self.behaviors["urgency"]["keywords"]
    return 1 if any(word in query.lower() for word in urgency_words) else 0

def groq_suggest(self):
    # As before, but with prompts.json for template selection
    template = random.choice(self.prompt_templates["suggestions"])
    prompt = template.format(logs=json.dumps(load_logs()))
    response = self.groq_client.client.chat.completions.create(
        model="mixtral-8x7b-32768", messages=[{"role": "user", "content": prompt}], max_tokens=200
    ).choices[0].message.content
    action = "increase_posts" if "increase" in response.lower() else "adjust_time"
    return {"text": response, "action": action}

async def implement_suggestion(self, action):
    # As before
    pass
