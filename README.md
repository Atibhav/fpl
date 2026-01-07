# FPL ML Team Builder 

A full-stack AI-powered assistant for Fantasy Premier League managers. This application uses Machine Learning to predict player points, optimize squads, and help you build the perfect team.

![Tech Stack](https://img.shields.io/badge/Stack-React%20|%20Spring%20Boot%20|%20Flask%20|%20PostgreSQL-blue)

##  Features

*   **🔮 AI Point Predictions:** Uses Random Forest and XGBoost models to predict player performance for upcoming gameweeks.
*   **🧠 Squad Optimizer:** Linear programming algorithm to generate the mathematically optimal team within your budget.
*   **📋 Interactive Team Planner:** Drag-and-drop interface to build and visualize your squad.
*   **📊 Fixture Difficulty Analysis:** Visual indicators for upcoming match difficulty.
*   **🔄 Auto-Updating Data:** Automatically fetches the latest match stats and retrains models daily.

##  Tech Stack

*   **Frontend:** React.js (deployed on Vercel)
*   **Backend:** Java Spring Boot (deployed on Render)
*   **ML Service:** Python Flask/FastAPI + Scikit-Learn (deployed on Render)
*   **Database:** PostgreSQL (hosted on Supabase)
*   **Data Source:** [FPL-Elo-Insights](https://github.com/olbauday/FPL-Elo-Insights)

##  Project Structure

*   `client/`: React frontend application.
*   `server/`: Spring Boot REST API backend.
*   `ml-service/`: Python Machine Learning service for predictions and optimization.
  

##  Getting Started (Local Dev)

### Prerequisites
*   Node.js & npm
*   Java JDK 17+
*   Python 3.10+
*   Docker (optional)

### 1. Clone the repo
```bash
git clone https://github.com/Atibhav/fpl.git
cd fpl
```

### 2. Start the ML Service
```bash
cd ml-service
pip install -r requirements.txt
python main.py
```

### 3. Start the Backend
```bash
cd server
./mvnw spring-boot:run
```

### 4. Start the Frontend
```bash
cd client
npm install
npm start
```


