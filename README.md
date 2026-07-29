---
title: MoodPlay
emoji: 🌿
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Transform your emotions into calming, browser-based mini-games using Hugging Face Transformers.
models:
  - j-hartmann/emotion-english-distilroberta-base
tags:
  - transformers
  - fastapi
  - emotion-classification
  - emotion-detection
  - nlp
  - machine-learning
  - ai
  - wellness
  - browser-game
---

# 🌿 MoodPlay

> **Transform your emotions into calming browser-based mini-games powered by AI.**

MoodPlay is an AI-powered web application that analyses a user's emotional state using a Hugging Face Transformers model and instantly generates a personalised calming mini-game. The goal is to encourage users to pause, relax, and reconnect through playful, interactive experiences.

**🚀 Live Demo:** https://huggingface.co/spaces/navk8690/moodplay

---

## ✨ Features

- 🧠 AI-powered emotion analysis using Hugging Face Transformers
- 🎮 Personalised browser-based mini-games
- 🌿 Calm botanical-inspired responsive interface
- ⚡ FastAPI backend
- 🔥 Local Transformer inference (no external inference API)
- 📱 Mobile-friendly design
- ❤️ Lightweight and privacy-friendly architecture

---

## 🛠️ Built With

### Backend

- Python 3.11
- FastAPI
- Uvicorn
- Hugging Face Transformers
- PyTorch

### Frontend

- HTML5
- CSS3
- JavaScript (Vanilla)

### AI Model

- **j-hartmann/emotion-english-distilroberta-base**

### Deployment

- Docker
- Hugging Face Spaces

---

## 🧠 How It Works

1. The user enters how they are feeling.
2. FastAPI sends the text to the local Transformer model.
3. The model predicts the dominant emotion.
4. MoodPlay selects a calming mini-game based on the detected emotion.
5. The game is displayed instantly in the browser.

```
User
   │
   ▼
FastAPI Backend
   │
   ▼
Hugging Face Transformer
   │
   ▼
Emotion Prediction
   │
   ▼
Mini-game Selection
   │
   ▼
Interactive Browser Game
```

---

## 🎮 Included Mini-Games

- ⭐ Catch the Stars
- 🧱 Break the Blocks
- ⚡ Quick Reaction
- 🌬️ Breathing Orbs
- 🌸 Gentle Garden
- 🧹 Clear the Space
- 🧠 Memory Match

---

## 📁 Project Structure

```text
moodplay/
├── app/
│   ├── __init__.py
│   └── main.py
├── static/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
├── Dockerfile
├── README.md
└── .gitignore
```

---

## 🚀 Running Locally

### Clone the repository

```bash
git clone https://github.com/navjotk8690/moodplay.git
cd moodplay
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate it

macOS / Linux

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
uvicorn app.main:app --reload
```

Open your browser:

```
http://localhost:8000
```

---

## 🐳 Running with Docker

Build the image

```bash
docker build -t moodplay .
```

Run the container

```bash
docker run -p 7860:7860 moodplay
```

Then open:

```
http://localhost:7860
```

---

## 📸 Screenshots

> *Add screenshots or GIFs here to showcase the interface and mini-games.*

---

## 💡 Future Improvements

- User authentication
- Mood history dashboard
- Additional emotion-based games
- Analytics
- Multiplayer relaxation games
- Multiple language support
- Accessibility improvements

---

## 📚 Technologies & Topics

- Artificial Intelligence
- Natural Language Processing
- Emotion Classification
- Emotion Detection
- Hugging Face Transformers
- FastAPI
- Machine Learning
- Browser Games
- Mental Wellness
- Docker
- Python

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- 🤗 Hugging Face
- FastAPI
- PyTorch
- The open-source AI community

---

## 👨‍💻 Author

**Navjot**

GitHub: https://github.com/navjotk8690/

Hugging Face: https://huggingface.co/navk8690