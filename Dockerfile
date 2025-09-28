FROM python:3.12-slim
RUN apt-get update && apt-get install -y chromium chromium-driver nodejs npm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY package.json .
RUN npm install
COPY . .
CMD ["python", "main.py"]
