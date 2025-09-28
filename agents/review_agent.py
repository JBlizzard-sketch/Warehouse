from groq import Groq
import random
from .content_agent import GroqClient

class ReviewAgent:
def init(self):
self.groq_client = GroqClient()

def generate_review(self, product_id):
    try:
        cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()[0]
        prompt = self.groq_client.prompt_templates["review"].format(product=product)
        review_text = self.groq_client.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        ).choices[0].message.content
        rating = random.randint(3, 5)
        cursor.execute("INSERT INTO reviews (product_id, review_text, rating, source) VALUES (?, ?, ?, ?)",
                      (product_id, review_text, rating, "generated"))
        conn.commit()
        return {"status": "success", "review": review_text}
    except Exception as e:
        return {"status": "error", "error": str(e)}
