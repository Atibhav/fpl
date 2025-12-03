# FPL ML Team Builder - Product Overview

## Project Scope & Vision

An intelligent Fantasy Premier League (FPL) team builder that combines **machine learning predictions** with **mathematical optimization** to help users select the best possible squad within FPL constraints. This is a full-stack web application showcasing modern development practices, ML engineering, and practical problem-solving for a resume/portfolio project targeting SDE roles.

---

## Problem Statement

Fantasy Premier League managers face a complex optimization problem:
- **650+ players** to choose from
- **£100m budget** constraint
- **Multiple position requirements** (2 GK, 5 DEF, 5 MID, 3 FWD)
- **Max 3 players per team** rule
- **Uncertain player performance** each gameweek
- **Transfer penalties** (-4 points per extra transfer)

Traditional approaches rely on gut feeling, form, and manual comparison. This project solves the problem systematically using data-driven predictions and constraint optimization.

---

## MVP FEATURES (Phase 1 - For Initial Deployment)

### 1. ML-Powered Points Prediction ✅

**What it does:** Predicts how many points each player will score next gameweek

**User benefit:** Make informed decisions based on data, not just intuition

**Technical approach:**
- Trains on 100K+ historical player-gameweek records (2016-2024)
- Uses ensemble ML models (Linear Regression, Random Forest, Support Vector Regression)
- Considers 15+ features: recent form, fixture difficulty, team strength, minutes played, home/away
- Handles new/promoted players by integrating external data (FBref scraping)

**Output:** Each player shows predicted points (e.g., "Haaland: 8.5 pts", "Salah: 7.2 pts")

---

### 2. Intelligent Squad Optimizer ✅

**What it does:** Automatically builds the optimal 15-player squad that maximizes expected points

**User benefit:** Find the mathematically best team in seconds, considering all 650+ players and 8+ constraints simultaneously

**Technical approach:**
- Linear Programming using PuLP library
- Optimizes across budget, positions, team limits
- Handles different scenarios:
  - Full squad (15 players)
  - Starting XI (11 players)
  - Custom budget constraints

**Output:** Complete squad with total cost (e.g., £99.5m) and expected points (e.g., 68.3 pts)

---

### 3. Interactive Team Planner ✅

**What it does:** Visual drag-and-drop interface to build, modify, and simulate your FPL team

**User benefit:** Intuitive squad building with live feedback on budget, points, and constraints

**Key features:**
- **Football pitch visualization** - See your team laid out in formation (4-3-3, 3-4-3, etc.)
- **Player search & filters** - Find players by name, position, team, price range
- **Budget tracker** - Live updates showing remaining budget
- **Predicted points display** - Each player card shows expected points (color-coded: green=high, red=low)
- **Squad validation** - Warns if you violate FPL rules (too many from one team, over budget, etc.)
- **Import team** - Enter FPL Team ID to fetch your current squad (no login required)

---

### 4. Fixture Difficulty Analysis ✅

**What it does:** Shows upcoming opponents for each team with difficulty ratings (1-5)

**User benefit:** Plan transfers ahead by targeting players with easy fixtures

**Features:**
- Visual fixture grid (next 5 gameweeks)
- Color-coded difficulty (green=easy, red=hard)
- Integrated into ML predictions (easy fixtures → higher predicted points)

---

## POST-MVP FEATURES (Phase 2 - After Initial Deployment)

### 5. Transfer Suggestions 🔄

**How it works:** Uses existing predicted points (no separate ML needed)

**Algorithm**:
1. Get predictions for all players
2. For each player in current squad, find best replacement in same position
3. Calculate points gain vs transfer cost (-4 penalty if no free transfers)
4. Sort by net gain
5. Return top 5 suggestions

**Example**: "OUT: Rashford (3.2 pts) → IN: Saka (7.5 pts) = +4.3 pts gain"

---

### 6. Chip Strategy Optimizer 🔄

- **Wildcard:** Full 15-player rebuild with no penalties
- **Free Hit:** One-week unlimited transfers
- **Bench Boost:** Include bench players in points optimization
- **Triple Captain:** 3x points for captain (high-confidence pick)

---

### 7. Model Performance Dashboard 🔄

**Purpose:** Resume showcase + transparency

**Metrics displayed:**
- RMSE, MAE, R² scores for each model
- Prediction accuracy over time
- Feature importance (which factors matter most)
- Comparison: Linear vs Random Forest vs Ensemble

---

### 8. Team Stats Explorer 🔄

**What it does:** Displays advanced team statistics (e.g., xG generated, xG conceded, possession) across a selectable range of gameweeks in a table format.

**User benefit:** Gives managers a high-level view of which teams are strong/weak offensively and defensively over specific periods (e.g., GW3–GW9), enabling better fixture- and form-based decisions.

**Planned capabilities:**
- Table with **one row per team** and **dynamic columns** for selected metrics:
  - xG For (expected goals created)
  - xG Against (expected goals conceded)
  - xG Difference (xGF - xGA)
  - Average Possession %
  - (Optionally) Shots For/Against, Big Chances, etc.
- **Filters:**
  - Gameweek range selector: from GW X to GW Y (default: GW1 → latest)
  - Presets: \"Full season\", \"Last 4 GWs\", \"Custom range\"
  - Individual gameweek selection (multi-select) as an advanced option
- **Aggregation options:**
  - Sum over selected GWs (e.g., total xG)
  - Per-game averages (e.g., xG per match, average possession)
- **Sorting:** Clickable column headers to sort teams by any metric (e.g., highest xG For, lowest xG Against).

**Data source approach (post-MVP, separate from core FPL API):**
- Use FBref or a similar public stats source to obtain **team-level per-match stats**:
  - Store in a `team_stats` table (PostgreSQL) via a one-time ETL script:
    - Columns: `team_id`, `season`, `gameweek`, `xg_for`, `xg_against`, `possession`, `shots_for`, `shots_against`, etc.
  - Optionally refresh once per week via a script, but not required for first version.

**Backend (Spring Boot) design:**
- New entity: `TeamStats` mapped to `team_stats` table.
- New repository: `TeamStatsRepository` with queries like:
  - `findBySeasonAndGameweekBetween(String season, int fromGw, int toGw)`
- New service: `TeamStatsService` to:
  - Aggregate stats by team over selected GWs (using `GROUP BY team_id`).
  - Compute totals and per-game averages.
- New controller: `TeamStatsController` with endpoints like:
  - `GET /api/team-stats?season=2025-26&fromGw=1&toGw=10&metrics=xg_for,xg_against,possession`
  - Returns JSON in the shape:
    ```json
    [
      {
        "teamName": "Arsenal",
        "gamesPlayed": 8,
        "xgFor": 15.2,
        "xgAgainst": 7.8,
        "xgDiff": 7.4,
        "possessionAvg": 61.3
      },
      ...
    ]
    ```

**Frontend (React) design:**
- New page: `/team-stats` (e.g., `TeamStatsPage.js`):
  - **Controls panel** (top):
    - From GW (number input or dropdown)
    - To GW (number input or dropdown)
    - Preset buttons (\"Season\", \"Last 4\", \"Custom\")
    - Metrics multi-select (checkboxes or multi-select dropdown)
  - **Stats table** (main area):
    - Row per team
    - Columns based on selected metrics
    - Column headers clickable to sort ascending/descending
    - Optional highlight for top/bottom teams per metric
- Shared React table component so this view feels consistent with other analytical pages.

**Integration with ML pipeline (optional, later):**
- These aggregated team stats can also be used as additional features for the ML models (offensive/defensive strength per team over recent GWs), but for post-MVP display they are primarily a **visual analytics feature**.

---

## USER WORKFLOWS (MVP)

### Workflow 1: Import Existing FPL Team (Primary Flow - Mid-Season)

1. Visit homepage → Click "Import My Team"
2. Enter FPL Team ID (e.g., 123456) - **No login required!**
3. System fetches current squad from public FPL API
4. View team on pitch with predicted points
5. Make manual changes OR click "Optimize" for suggestions
6. Save squad to MongoDB (optional)

**Note:** FPL API is public, no authentication needed. Anyone can fetch any team by ID.

**How to find FPL Team ID:**
- Go to fantasy.premierleague.com
- Click on "Points" or "View Gameweek history"
- Your Team ID is in the URL: `fantasy.premierleague.com/entry/123456/event/1`

---

### Workflow 2: Build Team from Scratch (Secondary Flow - Pre-Season/Experimentation)

1. Visit homepage → Click "Build New Team"
2. Browse players (filtered by position, team, price)
3. Click players to add to squad OR click "Optimize Squad" for auto-generation
4. Review suggested team on pitch visualization
5. Tweak manually if desired (swap players)
6. Save squad to MongoDB

**Use cases:**
- Pre-season planning before GW1
- Testing "what if" scenarios
- Building a completely new squad strategy

---

### Workflow 3: Weekly Captain Selection (Simple, Using Imported Team)

1. Import current team (via FPL ID)
2. View predicted points for next gameweek
3. System highlights highest predicted player
4. Consider fixture difficulty
5. Confirm captain choice

---

## TECHNICAL DIFFERENTIATORS (Resume Selling Points)

1. **End-to-End ML Pipeline:** Raw data → Feature engineering → Model training → Predictions → Production API
2. **Constraint Optimization:** Not just predictions, but optimal team selection with 8+ constraints using Linear Programming
3. **Microservices Architecture:** Separate Spring Boot (business logic/API) and Flask (ML) backends showing system design skills
4. **External Data Integration:** Solves cold-start problem by scraping Championship/European league stats (FBref)
5. **Real-time API Integration:** Live FPL data with Spring Cache abstraction (5-min TTL)
6. **Enterprise Stack:** Java/Spring Boot + React + Python ML (shows versatility and enterprise-grade development)
7. **Production Deployment:** Fully deployed app accessible online (not just localhost)
8. **Ensemble Learning:** Combines multiple ML algorithms (Linear Regression, Random Forest, SVR) for better accuracy
9. **RESTful API Design:** Well-structured REST controllers with proper HTTP semantics
10. **ORM/JPA:** Spring Data JPA for clean database abstraction and repository pattern

---

## SUCCESS METRICS

### User Metrics (Functional):
- Squad builder works for all valid FPL configurations
- Predictions within ±2 points RMSE
- Optimization completes in <5 seconds
- App loads in <3 seconds
- Handles 100+ concurrent users (free tier limits)

### Resume/Portfolio Metrics (What Matters for Jobs):
- Demonstrates 3+ ML algorithms from university coursework
- Shows full-stack capabilities (React + Express + Flask + MongoDB)
- Proves understanding of constraint optimization (Linear Programming)
- Evidence of production deployment on free hosting
- Clean, documented code on GitHub
- Live demo link in resume

---

## PROJECT SCOPE SUMMARY

### ✅ INCLUDED IN MVP:
- ML prediction models (Linear Regression, Random Forest, SVR, Ensemble)
- Linear programming optimization (PuLP)
- Interactive squad builder UI with pitch view
- Team import from FPL API (public, no auth)
- Fixture difficulty analysis
- Save/load squads (MongoDB)
- Deployment to free hosting

### 🔄 POST-MVP (Phase 2):
- Transfer suggestions (uses existing predictions)
- Chip strategy optimizer
- Model performance dashboard
- Weekly model retraining automation
- Team stats explorer (xG/xGA, possession, etc. per team with gameweek filters)

### ❌ NOT INCLUDED (Out of Scope):
- User authentication/accounts (not needed, FPL API is public)
- Social features (share teams, leagues)
- Historical tracking (your team's performance over season)
- Mobile app (React Native)
- Real-time push notifications
- Advanced features (differential picks, template teams)

---

## RESUME TALKING POINTS

**Project Description:**
> "Full-stack Fantasy Premier League team optimization app using machine learning and linear programming to predict player points and generate optimal squads within budget and position constraints."

**Technical Highlights:**
- "Trained ensemble ML model (Linear Regression, Random Forest, SVR) on 100K+ historical data points achieving X RMSE"
- "Implemented linear programming optimization using PuLP with 8+ constraints to maximize expected points"
- "Built microservices architecture: Spring Boot REST API for business logic, Flask API for ML predictions"
- "Designed responsive React frontend with interactive drag-and-drop team builder"
- "Integrated external data scraping (FBref) to solve cold-start problem for new players"
- "Deployed full-stack application on Render.com with Docker containerization (React Static Site + Spring Boot + Flask + PostgreSQL)"
- "Implemented RESTful API with Spring Boot using proper layered architecture (Controller-Service-Repository)"

**Key Concepts Demonstrated:**
- **Backend:** Java, Spring Boot, Spring Data JPA, REST APIs, ORM, dependency injection
- **Machine Learning:** Supervised learning, regression, ensemble methods, feature engineering
- **Optimization:** Linear programming, constraint satisfaction
- **Frontend:** React, component architecture, state management, API integration
- **Database:** PostgreSQL, JPA entities, repository pattern
- **Data Engineering:** ETL pipeline, data preprocessing, external API integration
- **DevOps:** Docker, deployment, environment management, microservices

---

## KEY LEARNING INSIGHTS FROM RESEARCH

Based on successful FPL ML projects (Sasank Channapragada's 7-year project):

### What Works:
1. ✅ **Ensemble methods** (Voting Regressor) - combining multiple models is better than any single model
2. ✅ **Form-based features** - recent performance (last 3-5 games) is highly predictive
3. ✅ **Fixture difficulty** - opposition strength matters significantly
4. ✅ **Iterative improvement** - start simple, add complexity based on results

### Cold Start Problem Solution:
- Use FBref data for new/promoted players
- Map Championship/European league stats to Premier League level
- Apply difficulty multipliers (Championship × 0.7, La Liga × 0.9, etc.)
- Fallback to similarity matching if external data unavailable

### Model Prioritization:
- Focus on **Voting Regressor** combining Linear Regression, SVR, Random Forest
- Skip Neural Networks if ensemble already performs well (simpler is better)
- Position-specific models (separate for GK, DEF, MID, FWD) improve accuracy

---

## DEPLOYMENT STRATEGY (All on Render.com - FREE)

| Component | Render Service Type | Free Tier Details | Cost |
|-----------|---------------------|-------------------|------|
| **React Frontend** | Static Site | Unlimited bandwidth, SSL, custom domain | $0 |
| **Spring Boot Backend** | Web Service (Docker) | 750 hrs/month shared | $0 |
| **Flask ML Service** | Web Service (Python) | 750 hrs/month shared | $0 |
| **PostgreSQL** | PostgreSQL | 1GB storage, 90-day expiry | $0 |

**Total monthly cost: $0**

**Single Platform Benefits:**
- One dashboard to manage all services
- Easy environment variable sharing (internal URLs)
- Simplified deployment workflow
- All services in same region = lower latency

**Note:** Free web services sleep after 15 min inactivity, wake on request (~30s cold start).

---

## NEXT STEPS

Ready to implement! Follow the technical plan in the main plan document for step-by-step implementation:

1. Backend setup (Express + Flask)
2. Data pipeline (Vaastav + FBref)
3. ML models (Linear Regression → Ensemble)
4. Optimization (PuLP)
5. Frontend (React components)
6. Integration & deployment

# TECHNICAL PLAN

# FPL ML-Powered Team Builder

## Tech Stack (100% Free)

- **Frontend**: React with JavaScript, CSS/TailwindCSS
- **Backend API**: Java 17+ with Spring Boot 3.x
  - Handles user data, saved squads, REST API
  - Spring Data JPA for database access
  - PostgreSQL database
- **ML/Optimization Backend**: Flask (Python)
  - Separate microservice for ML predictions and PuLP optimization
  - Only handles computationally heavy ML tasks
- **Data**: Vaastav's FPL dataset (GitHub, free) + Official FPL API (free, no key required)
- **Deployment** (All on Render.com):
  - Frontend (React): Render.com Static Site (free)
  - Java Backend: Render.com Web Service (free tier)
  - Flask ML Service: Render.com Web Service (free tier) 
  - PostgreSQL: Render.com PostgreSQL (free tier, 1GB, 90-day expiry - can recreate)

**All services are FREE on Render.com - single platform for everything**

## Architecture Overview

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│   React     │─────▶│  Spring Boot +   │─────▶│  FPL API    │
│  Frontend   │      │  PostgreSQL      │      │  (Free)     │
└─────────────┘      └──────────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────────┐
                     │  Flask ML API    │
                     │  (Predictions    │
                     │   + PuLP)        │
                     └──────────────────┘
```

**Why this architecture?**

- React handles all UI/UX (squad builder, visualizations)
- Spring Boot handles REST API, business logic, data persistence (saved squads)
- Flask handles ONLY ML predictions and optimization (Python is better for ML libraries)
- Spring Boot calls Flask internally when predictions needed via RestTemplate/WebClient
- User never directly interacts with Flask

## Phase 1: Project Setup

### 1.1 Backend Setup - Spring Boot (`/backend`)

**Learning**: Spring Boot basics, REST APIs, JPA, PostgreSQL

Initialize Spring Boot project using Spring Initializr (https://start.spring.io/):

**Configuration:**
- Project: Maven
- Language: Java
- Spring Boot: 3.2.x (latest stable)
- Java: 17 or 21
- Dependencies:
  - Spring Web
  - Spring Data JPA
  - PostgreSQL Driver
  - Lombok (optional, reduces boilerplate)
  - Validation

Or use command line:

```bash
mkdir backend
cd backend
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,postgresql,lombok,validation \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.2.0 \
  -d baseDir=backend \
  -d groupId=com.fpl \
  -d artifactId=fpl-backend \
  -o backend.zip && unzip backend.zip && rm backend.zip
```

Project structure:

```
/backend
├── pom.xml                           # Maven dependencies
├── src/main/java/com/fpl/fplbackend/
│   ├── FplBackendApplication.java   # Main Spring Boot class
│   ├── /controller                  # REST Controllers
│   │   ├── PlayerController.java
│   │   ├── SquadController.java
│   │   └── FplController.java
│   ├── /service                     # Business logic
│   │   ├── PlayerService.java
│   │   ├── SquadService.java
│   │   ├── FplApiService.java
│   │   └── MLServiceClient.java
│   ├── /model                       # JPA Entities
│   │   └── Squad.java
│   ├── /repository                  # JPA Repositories
│   │   └── SquadRepository.java
│   ├── /dto                         # Data Transfer Objects
│   │   ├── PlayerDTO.java
│   │   └── SquadDTO.java
│   └── /config                      # Configuration
│       └── CorsConfig.java
└── src/main/resources/
    └── application.properties       # Configuration
```

**`application.properties`** - Configuration:

```properties
# Server Configuration
server.port=8080

# Database Configuration (PostgreSQL)
spring.datasource.url=jdbc:postgresql://localhost:5432/fpldb
spring.datasource.username=postgres
spring.datasource.password=yourpassword
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

# ML Service Configuration
ml.service.url=http://localhost:5001

# FPL API Configuration
fpl.api.base-url=https://fantasy.premierleague.com/api
fpl.api.cache-duration=300000
```

**`Squad.java`** - JPA Entity:

```java
package com.fpl.fplbackend.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "squads")
@Data
public class Squad {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String userId;  // Optional: for user accounts later
    private String name;
    private Double budget;
    private Double expectedPoints;
    
    @ElementCollection
    @CollectionTable(name = "squad_players", joinColumns = @JoinColumn(name = "squad_id"))
    private List<SquadPlayer> players;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Embeddable
    @Data
    public static class SquadPlayer {
        private Integer playerId;
        private String name;
        private String position;
        private Double price;
        private Boolean isStarter;
        private Boolean isCaptain;
    }
}
```

**`SquadRepository.java`** - JPA Repository:

```java
package com.fpl.fplbackend.repository;

import com.fpl.fplbackend.model.Squad;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SquadRepository extends JpaRepository<Squad, Long> {
    List<Squad> findByUserIdOrderByCreatedAtDesc(String userId);
}
```

**`CorsConfig.java`** - Enable CORS for React:

```java
package com.fpl.fplbackend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig {
    
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                        .allowedOrigins("http://localhost:3000") // React dev server
                        .allowedMethods("GET", "POST", "PUT", "DELETE")
                        .allowedHeaders("*");
            }
        };
    }
}
```

### 1.2 Flask ML Backend (`/ml-service`)

**Learning**: Flask basics, Python ML libraries

Initialize Flask app:

```bash
mkdir ml-service
cd ml-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask-cors pandas numpy scikit-learn tensorflow pulp requests
pip freeze > requirements.txt
```

Project structure:

```
/ml-service
├── app.py                    # Flask entry point
├── requirements.txt
├── /ml
│   ├── baseline_models.py    # Linear Regression
│   ├── advanced_models.py    # Neural Net, Ensemble
│   ├── train_models.py       # Training pipeline
│   └── predictor.py          # Prediction service
├── /optimization
│   └── team_optimizer.py     # PuLP optimization
├── /data
│   ├── data_processor.py     # Preprocessing
│   └── /raw                  # Vaastav's dataset
└── /models                   # Saved .pkl models
```

**`app.py`** - Flask app:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from ml.predictor import predict_players
from optimization.team_optimizer import optimize_squad

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    players = request.json['players']
    predictions = predict_players(players)
    return jsonify(predictions)

@app.route('/optimize/squad', methods=['POST'])
def optimize():
    data = request.json
    result = optimize_squad(data['players'], data['budget'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
```

### 1.3 Frontend Setup - React (`/frontend`)

**Learning**: React basics, component structure, API calls

Initialize React app:

```bash
npx create-react-app frontend
cd frontend
npm install axios react-router-dom
npm install -D tailwindcss
```

Project structure:

```
/frontend
├── package.json
├── /src
│   ├── App.js              # Main app component
│   ├── index.js            # Entry point
│   ├── /components
│   │   ├── PlayerCard.js
│   │   ├── PitchView.js
│   │   ├── SquadBuilder.js
│   │   ├── PredictionPanel.js
│   │   └── OptimizationPanel.js
│   ├── /pages
│   │   ├── Home.js
│   │   ├── Planner.js
│   │   ├── Predictions.js
│   │   └── MyTeam.js
│   ├── /services
│   │   └── api.js          # API calls to Express backend
│   └── /styles
│       └── App.css
└── /public
```

**`src/services/api.js`** - API wrapper:

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const getPlayers = async () => {
  const response = await axios.get(`${API_BASE}/players`);
  return response.data;
};

export const optimizeSquad = async (budget) => {
  const response = await axios.post(`${API_BASE}/squads/optimize`, { budget });
  return response.data;
};

export const saveSquad = async (squad) => {
  const response = await axios.post(`${API_BASE}/squads`, squad);
  return response.data;
};
```

## Phase 2: Data Pipeline

### 2.1 FPL API Integration (`FplApiService.java`)

**Learning**: REST APIs, RestTemplate/WebClient, Caching

```java
package com.fpl.fplbackend.service;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Service
public class FplApiService {
    
    @Value("${fpl.api.base-url}")
    private String fplBaseUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    @Cacheable(value = "players", unless = "#result == null")
    public List<Map<String, Object>> getAllPlayers() {
        String url = fplBaseUrl + "/bootstrap-static/";
        
        try {
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            return (List<Map<String, Object>>) response.get("elements");
        } catch (Exception e) {
            throw new RuntimeException("Failed to fetch players from FPL API", e);
        }
    }
    
    public Map<String, Object> getUserTeam(String fplId) {
        String url = fplBaseUrl + "/entry/" + fplId + "/";
        
        try {
            return restTemplate.getForObject(url, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to fetch team for ID: " + fplId, e);
        }
    }
    
    public Map<String, Object> getUserPicks(String fplId, int gameweek) {
        String url = fplBaseUrl + "/entry/" + fplId + "/event/" + gameweek + "/picks/";
        
        try {
            return restTemplate.getForObject(url, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to fetch picks for ID: " + fplId, e);
        }
    }
    
    @Cacheable(value = "fixtures", unless = "#result == null")
    public List<Map<String, Object>> getFixtures() {
        String url = fplBaseUrl + "/fixtures/";
        
        try {
            return restTemplate.getForObject(url, List.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to fetch fixtures from FPL API", e);
        }
    }
    
    public int getCurrentGameweek() {
        String url = fplBaseUrl + "/bootstrap-static/";
        
        try {
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            List<Map<String, Object>> events = (List<Map<String, Object>>) response.get("events");
            
            return events.stream()
                    .filter(event -> (Boolean) event.get("is_current"))
                    .findFirst()
                    .map(event -> (Integer) event.get("id"))
                    .orElse(1);
        } catch (Exception e) {
            return 1; // Default to gameweek 1
        }
    }
}
```

**Enable Caching** - Add to `FplBackendApplication.java`:

```java
package com.fpl.fplbackend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class FplBackendApplication {
    public static void main(String[] args) {
        SpringApplication.run(FplBackendApplication.class, args);
    }
}
```

### 2.2 Player Controller (`PlayerController.java`)

```java
package com.fpl.fplbackend.controller;

import com.fpl.fplbackend.service.FplApiService;
import com.fpl.fplbackend.service.MLServiceClient;
import com.fpl.fplbackend.service.PlayerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/players")
public class PlayerController {
    
    @Autowired
    private FplApiService fplApiService;
    
    @Autowired
    private MLServiceClient mlServiceClient;
    
    @Autowired
    private PlayerService playerService;
    
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getAllPlayers() {
        try {
            // Fetch players from FPL API
            List<Map<String, Object>> players = fplApiService.getAllPlayers();
            
            // Get predictions from ML service
            Map<String, Double> predictions = mlServiceClient.getPredictions(players);
            
            // Merge predictions with player data
            List<Map<String, Object>> enrichedPlayers = playerService.enrichPlayersWithPredictions(players, predictions);
            
            return ResponseEntity.ok(enrichedPlayers);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getPlayer(@PathVariable Integer id) {
        try {
            List<Map<String, Object>> allPlayers = fplApiService.getAllPlayers();
            Map<String, Object> player = allPlayers.stream()
                    .filter(p -> p.get("id").equals(id))
                    .findFirst()
                    .orElseThrow(() -> new RuntimeException("Player not found"));
            
            return ResponseEntity.ok(player);
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
}
```

**`PlayerService.java`** - Business Logic:

```java
package com.fpl.fplbackend.service;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class PlayerService {
    
    public List<Map<String, Object>> enrichPlayersWithPredictions(
            List<Map<String, Object>> players,
            Map<String, Double> predictions) {
        
        return players.stream()
                .map(player -> {
                    Integer playerId = (Integer) player.get("id");
                    player.put("predicted_points", predictions.getOrDefault(String.valueOf(playerId), 0.0));
                    return player;
                })
                .collect(Collectors.toList());
    }
}
```

### 2.3 ML Service Client (`MLServiceClient.java`)

Spring Boot calls Flask for ML predictions:

```java
package com.fpl.fplbackend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MLServiceClient {
    
    @Value("${ml.service.url}")
    private String mlServiceUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    public Map<String, Double> getPredictions(List<Map<String, Object>> players) {
        String url = mlServiceUrl + "/predict";
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("players", players);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            Map<String, Double> response = restTemplate.postForObject(url, request, Map.class);
            return response != null ? response : new HashMap<>();
            
        } catch (Exception e) {
            System.err.println("ML Service error: " + e.getMessage());
            return new HashMap<>(); // Return empty if ML service is down
        }
    }
    
    public Map<String, Object> optimizeSquad(List<Map<String, Object>> players, Double budget) {
        String url = mlServiceUrl + "/optimize/squad";
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("players", players);
            requestBody.put("budget", budget);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            return restTemplate.postForObject(url, request, Map.class);
            
        } catch (Exception e) {
            throw new RuntimeException("Optimization failed: " + e.getMessage(), e);
        }
    }
}
```

### 2.4 Vaastav Dataset Processing (`/ml-service/data/data_processor.py`)

**Learning**: Data preprocessing, feature engineering, pandas

Download dataset:

```bash
cd ml-service/data/raw
git clone https://github.com/vaastav/Fantasy-Premier-League.git
```

**`data_processor.py`**:

```python
import pandas as pd
import numpy as np
from datetime import datetime

def load_historical_data(seasons=['2021-22', '2022-23', '2023-24']):
    """Load player data from multiple seasons"""
    all_data = []
    
    for season in seasons:
        path = f'raw/Fantasy-Premier-League/data/{season}/gws/merged_gw.csv'
        df = pd.read_csv(path)
        df['season'] = season
        all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True)

def clean_data(df):
    """Handle missing values and remove duplicates"""
    # Remove rows with missing target variable
    df = df.dropna(subset=['total_points'])
    
    # Fill missing numeric values with 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    return df

def encode_features(df):
    """Convert categorical features to numeric"""
    # Position encoding
    position_map = {'GK': 0, 'DEF': 1, 'MID': 2, 'FWD': 3}
    df['position_encoded'] = df['position'].map(position_map)
    
    # Team encoding (assign unique IDs)
    df['team_id'] = df['team'].astype('category').cat.codes
    df['opponent_id'] = df['opponent_team'].astype('category').cat.codes
    
    # Home/away encoding
    df['is_home'] = (df['was_home'] == True).astype(int)
    
    # Parse kickoff time
    df['kickoff_time'] = pd.to_datetime(df['kickoff_time'])
    df['month'] = df['kickoff_time'].dt.month
    df['day_of_week'] = df['kickoff_time'].dt.dayofweek
    df['hour'] = df['kickoff_time'].dt.hour
    
    return df

def engineer_features(df):
    """Create rolling statistics and derived features"""
    # Sort by player and date
    df = df.sort_values(['name', 'kickoff_time'])
    
    # Rolling averages (last 3 games)
    df['last_3_avg_points'] = df.groupby('name')['total_points'].transform(
        lambda x: x.rolling(3, min_periods=1).mean().shift(1)
    )
    
    # Rolling averages (last 5 games)
    df['last_5_avg_points'] = df.groupby('name')['total_points'].transform(
        lambda x: x.rolling(5, min_periods=1).mean().shift(1)
    )
    
    # Minutes per game
    df['minutes_per_game'] = df.groupby('name')['minutes'].transform(
        lambda x: x.rolling(5, min_periods=1).mean()
    )
    
    # Goals/assists per 90 minutes
    df['goals_per_90'] = (df['goals_scored'] / df['minutes'] * 90).fillna(0)
    df['assists_per_90'] = (df['assists'] / df['minutes'] * 90).fillna(0)
    
    return df

def prepare_training_data(df):
    """Prepare X (features) and y (target)"""
    feature_columns = [
        'position_encoded', 'team_id', 'opponent_id', 'is_home',
        'last_3_avg_points', 'last_5_avg_points', 'minutes_per_game',
        'value', 'goals_per_90', 'assists_per_90',
        'month', 'day_of_week'
    ]
    
    X = df[feature_columns]
    y = df['total_points']
    
    return X, y

# Main pipeline
def process_data():
    print("Loading data...")
    df = load_historical_data()
    
    print("Cleaning data...")
    df = clean_data(df)
    
    print("Encoding features...")
    df = encode_features(df)
    
    print("Engineering features...")
    df = engineer_features(df)
    
    print("Preparing training data...")
    X, y = prepare_training_data(df)
    
    return X, y, df

if __name__ == '__main__':
    X, y, df = process_data()
    print(f"Dataset shape: {X.shape}")
    print(f"Features: {X.columns.tolist()}")
    
    # Save processed data
    df.to_csv('processed_data.csv', index=False)
```

## Phase 3: ML Models (University Concepts)

### 3.1 Baseline Model - Linear Regression (`/ml-service/ml/baseline_models.py`)

**Learning**: Supervised learning, regression, model evaluation

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import joblib

def train_linear_regression(X, y, position='ALL'):
    """Train Linear Regression model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Position: {position}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"R²: {r2:.2f}")
    
    # Save model
    joblib.dump(model, f'../models/linear_regression_{position}.pkl')
    
    return model, {'rmse': rmse, 'mae': mae, 'r2': r2}

def train_position_specific_models(df):
    """Train separate models for each position"""
    positions = ['GK', 'DEF', 'MID', 'FWD']
    models = {}
    metrics = {}
    
    for pos in positions:
        pos_df = df[df['position'] == pos]
        X = pos_df[feature_columns]
        y = pos_df['total_points']
        
        model, metric = train_linear_regression(X, y, position=pos)
        models[pos] = model
        metrics[pos] = metric
    
    return models, metrics
```

### 3.2 Advanced Models (`/ml-service/ml/advanced_models.py`)

**Neural Network (MLP)** using TensorFlow:

```python
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler

def build_neural_network(input_dim):
    """Build MLP architecture"""
    model = keras.Sequential([
        keras.layers.Input(shape=(input_dim,)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(1, activation='linear')  # Output: predicted points
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model

def train_neural_network(X, y):
    """Train Neural Network"""
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X_scaled, y, test_size=0.15, random_state=42
    )
    
    # Build model
    model = build_neural_network(X.shape[1])
    
    # Early stopping
    early_stop = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1
    )
    
    # Save
    model.save('../models/neural_network.h5')
    joblib.dump(scaler, '../models/scaler.pkl')
    
    return model, scaler
```

**Random Forest Ensemble**:

```python
from sklearn.ensemble import RandomForestRegressor

def train_random_forest(X, y):
    """Train Random Forest ensemble"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Random Forest RMSE: {rmse:.2f}")
    
    # Save
    joblib.dump(model, '../models/random_forest.pkl')
    
    return model
```

### 3.3 Training Script (`/ml-service/ml/train_models.py`)

**Run this once to train all models**:

```python
import sys
sys.path.append('..')

from data.data_processor import process_data
from baseline_models import train_position_specific_models
from advanced_models import train_neural_network, train_random_forest

def main():
    print("=" * 50)
    print("FPL ML Model Training Pipeline")
    print("=" * 50)
    
    # Load and process data
    X, y, df = process_data()
    
    # Train baseline models
    print("\n1. Training Linear Regression models...")
    linear_models, linear_metrics = train_position_specific_models(df)
    
    # Train neural network
    print("\n2. Training Neural Network...")
    nn_model, scaler = train_neural_network(X, y)
    
    # Train ensemble
    print("\n3. Training Random Forest...")
    rf_model = train_random_forest(X, y)
    
    print("\n" + "=" * 50)
    print("Training complete! Models saved to /models/")
    print("=" * 50)

if __name__ == '__main__':
    main()
```

### 3.4 Prediction Service (`/ml-service/ml/predictor.py`)

```python
import joblib
import numpy as np
from tensorflow import keras

# Load models once at startup
linear_models = {
    'GK': joblib.load('../models/linear_regression_GK.pkl'),
    'DEF': joblib.load('../models/linear_regression_DEF.pkl'),
    'MID': joblib.load('../models/linear_regression_MID.pkl'),
    'FWD': joblib.load('../models/linear_regression_FWD.pkl'),
}
nn_model = keras.models.load_model('../models/neural_network.h5')
rf_model = joblib.load('../models/random_forest.pkl')
scaler = joblib.load('../models/scaler.pkl')

def predict_player(player_features, position):
    """Predict points for a single player using ensemble"""
    # Linear model prediction
    linear_pred = linear_models[position].predict([player_features])[0]
    
    # Neural network prediction
    scaled_features = scaler.transform([player_features])
    nn_pred = nn_model.predict(scaled_features, verbose=0)[0][0]
    
    # Random forest prediction
    rf_pred = rf_model.predict([player_features])[0]
    
    # Ensemble: average of all three
    ensemble_pred = (linear_pred + nn_pred + rf_pred) / 3
    
    return {
        'linear': float(linear_pred),
        'neural_network': float(nn_pred),
        'random_forest': float(rf_pred),
        'ensemble': float(ensemble_pred)
    }

def predict_players(players):
    """Predict points for list of players"""
    predictions = {}
    
    for player in players:
        # Extract features (you'll need to format player data properly)
        features = extract_features(player)
        position = player['position']
        
        pred = predict_player(features, position)
        predictions[player['id']] = pred['ensemble']
    
    return predictions
```

## Phase 4: Optimization Engine (PuLP)

**File**: `/ml-service/optimization/team_optimizer.py`

```python
from pulp import *

def optimize_squad(players_with_predictions, budget=100.0):
    """
    Optimize squad selection using Linear Programming
    
    Args:
        players_with_predictions: List of dicts with player data + predicted_points
        budget: Maximum budget (default 100.0)
    
    Returns:
        Optimal squad of 15 players
    """
    # Create optimization problem
    prob = LpProblem("FPL_Squad_Selection", LpMaximize)
    
    # Decision variables: x[i] = 1 if player i is selected
    player_vars = {}
    for player in players_with_predictions:
        player_vars[player['id']] = LpVariable(
            f"player_{player['id']}", 
            cat='Binary'
        )
    
    # Objective: Maximize total predicted points
    prob += lpSum([
        players_with_predictions[i]['predicted_points'] * player_vars[player['id']]
        for i, player in enumerate(players_with_predictions)
    ])
    
    # Constraint 1: Exactly 15 players
    prob += lpSum([player_vars[p['id']] for p in players_with_predictions]) == 15
    
    # Constraint 2: Budget limit
    prob += lpSum([
        p['price'] * player_vars[p['id']] 
        for p in players_with_predictions
    ]) <= budget
    
    # Constraint 3: Exactly 2 goalkeepers
    gk_players = [p for p in players_with_predictions if p['position'] == 'GK']
    prob += lpSum([player_vars[p['id']] for p in gk_players]) == 2
    
    # Constraint 4: Exactly 5 defenders
    def_players = [p for p in players_with_predictions if p['position'] == 'DEF']
    prob += lpSum([player_vars[p['id']] for p in def_players]) == 5
    
    # Constraint 5: Exactly 5 midfielders
    mid_players = [p for p in players_with_predictions if p['position'] == 'MID']
    prob += lpSum([player_vars[p['id']] for p in mid_players]) == 5
    
    # Constraint 6: Exactly 3 forwards
    fwd_players = [p for p in players_with_predictions if p['position'] == 'FWD']
    prob += lpSum([player_vars[p['id']] for p in fwd_players]) == 3
    
    # Constraint 7: Max 3 players per team
    teams = set(p['team'] for p in players_with_predictions)
    for team in teams:
        team_players = [p for p in players_with_predictions if p['team'] == team]
        prob += lpSum([player_vars[p['id']] for p in team_players]) <= 3
    
    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))  # Silent solver
    
    # Extract selected players
    selected_squad = []
    total_cost = 0
    total_expected_points = 0
    
    for player in players_with_predictions:
        if player_vars[player['id']].varValue == 1:
            selected_squad.append(player)
            total_cost += player['price']
            total_expected_points += player['predicted_points']
    
    return {
        'squad': selected_squad,
        'total_cost': total_cost,
        'expected_points': total_expected_points,
        'status': LpStatus[prob.status]
    }
```

## Phase 5: React Frontend

### 5.1 Main Components

**`PlayerCard.js`** - Display player card:

```javascript
import React from 'react';
import './PlayerCard.css';

function PlayerCard({ player, onSelect, isSelected }) {
  const getColorByPoints = (points) => {
    if (points >= 6) return 'green';
    if (points >= 4) return 'yellow';
    return 'red';
  };
  
  return (
    <div 
      className={`player-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(player)}
    >
      <div className="player-name">{player.name}</div>
      <div className="player-team">{player.team}</div>
      <div className="player-position">{player.position}</div>
      <div className="player-price">£{player.price}m</div>
      <div 
        className="predicted-points"
        style={{ color: getColorByPoints(player.predicted_points) }}
      >
        {player.predicted_points.toFixed(1)} pts
      </div>
    </div>
  );
}

export default PlayerCard;
```

**`SquadBuilder.js`** - Main team planner:

```javascript
import React, { useState, useEffect } from 'react';
import { getPlayers, optimizeSquad as apiOptimizeSquad } from '../services/api';
import PlayerCard from './PlayerCard';
import PitchView from './PitchView';

function SquadBuilder() {
  const [allPlayers, setAllPlayers] = useState([]);
  const [selectedSquad, setSelectedSquad] = useState([]);
  const [budget, setBudget] = useState(100.0);
  const [filter, setFilter] = useState({ position: 'ALL', search: '' });
  
  useEffect(() => {
    loadPlayers();
  }, []);
  
  const loadPlayers = async () => {
    const players = await getPlayers();
    setAllPlayers(players);
  };
  
  const handleSelectPlayer = (player) => {
    if (selectedSquad.find(p => p.id === player.id)) {
      // Remove player
      setSelectedSquad(selectedSquad.filter(p => p.id !== player.id));
      setBudget(budget + player.price);
    } else {
      // Add player
      if (selectedSquad.length < 15 && budget >= player.price) {
        setSelectedSquad([...selectedSquad, player]);
        setBudget(budget - player.price);
      }
    }
  };
  
  const handleOptimize = async () => {
    const result = await apiOptimizeSquad(budget + calculateSquadCost());
    setSelectedSquad(result.squad);
    setBudget(100.0 - result.total_cost);
  };
  
  const calculateSquadCost = () => {
    return selectedSquad.reduce((sum, p) => sum + p.price, 0);
  };
  
  const filteredPlayers = allPlayers.filter(p => {
    if (filter.position !== 'ALL' && p.position !== filter.position) return false;
    if (filter.search && !p.name.toLowerCase().includes(filter.search.toLowerCase())) return false;
    return true;
  });
  
  return (
    <div className="squad-builder">
      <div className="left-panel">
        <h2>Players</h2>
        <input 
          type="text"
          placeholder="Search players..."
          onChange={(e) => setFilter({...filter, search: e.target.value})}
        />
        <select onChange={(e) => setFilter({...filter, position: e.target.value})}>
          <option value="ALL">All Positions</option>
          <option value="GK">Goalkeepers</option>
          <option value="DEF">Defenders</option>
          <option value="MID">Midfielders</option>
          <option value="FWD">Forwards</option>
        </select>
        
        <div className="player-list">
          {filteredPlayers.map(player => (
            <PlayerCard 
              key={player.id}
              player={player}
              onSelect={handleSelectPlayer}
              isSelected={selectedSquad.find(p => p.id === player.id)}
            />
          ))}
        </div>
      </div>
      
      <div className="center-panel">
        <PitchView squad={selectedSquad} />
      </div>
      
      <div className="right-panel">
        <h2>Squad Summary</h2>
        <p>Budget Remaining: £{budget.toFixed(1)}m</p>
        <p>Players: {selectedSquad.length}/15</p>
        <button onClick={handleOptimize}>Optimize Squad</button>
      </div>
    </div>
  );
}

export default SquadBuilder;
```

**`PitchView.js`** - Pitch visualization:

```javascript
import React from 'react';
import './PitchView.css';

function PitchView({ squad }) {
  const positions = {
    GK: squad.filter(p => p.position === 'GK').slice(0, 1),
    DEF: squad.filter(p => p.position === 'DEF').slice(0, 5),
    MID: squad.filter(p => p.position === 'MID').slice(0, 5),
    FWD: squad.filter(p => p.position === 'FWD').slice(0, 3)
  };
  
  return (
    <div className="pitch">
      <div className="position-row">
        {positions.FWD.map(player => (
          <div key={player.id} className="player-on-pitch">
            {player.name.split(' ').pop()}
          </div>
        ))}
      </div>
      <div className="position-row">
        {positions.MID.map(player => (
          <div key={player.id} className="player-on-pitch">
            {player.name.split(' ').pop()}
          </div>
        ))}
      </div>
      <div className="position-row">
        {positions.DEF.map(player => (
          <div key={player.id} className="player-on-pitch">
            {player.name.split(' ').pop()}
          </div>
        ))}
      </div>
      <div className="position-row">
        {positions.GK.map(player => (
          <div key={player.id} className="player-on-pitch">
            {player.name.split(' ').pop()}
          </div>
        ))}
      </div>
    </div>
  );
}

export default PitchView;
```

## Phase 6: PostgreSQL Integration with Spring Data JPA

**Squad Controller** - `/backend/src/.../controller/SquadController.java`:

```java
package com.fpl.fplbackend.controller;

import com.fpl.fplbackend.model.Squad;
import com.fpl.fplbackend.service.SquadService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/squads")
public class SquadController {
    
    @Autowired
    private SquadService squadService;
    
    // GET all saved squads
    @GetMapping
    public ResponseEntity<List<Squad>> getAllSquads() {
        List<Squad> squads = squadService.getAllSquads();
        return ResponseEntity.ok(squads);
    }
    
    // GET squad by ID
    @GetMapping("/{id}")
    public ResponseEntity<Squad> getSquadById(@PathVariable Long id) {
        return squadService.getSquadById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    // POST save new squad
    @PostMapping
    public ResponseEntity<Squad> saveSquad(@RequestBody Squad squad) {
        Squad savedSquad = squadService.saveSquad(squad);
        return ResponseEntity.ok(savedSquad);
    }
    
    // DELETE squad
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> deleteSquad(@PathVariable Long id) {
        squadService.deleteSquad(id);
        return ResponseEntity.ok(Map.of("message", "Squad deleted"));
    }
    
    // POST optimize squad (calls ML service)
    @PostMapping("/optimize")
    public ResponseEntity<Map<String, Object>> optimizeSquad(@RequestBody Map<String, Object> request) {
        try {
            Double budget = (Double) request.get("budget");
            Map<String, Object> result = squadService.optimizeSquad(budget);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}
```

**Squad Service** - `/backend/src/.../service/SquadService.java`:

```java
package com.fpl.fplbackend.service;

import com.fpl.fplbackend.model.Squad;
import com.fpl.fplbackend.repository.SquadRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class SquadService {
    
    @Autowired
    private SquadRepository squadRepository;
    
    @Autowired
    private FplApiService fplApiService;
    
    @Autowired
    private MLServiceClient mlServiceClient;
    
    public List<Squad> getAllSquads() {
        return squadRepository.findAll();
    }
    
    public Optional<Squad> getSquadById(Long id) {
        return squadRepository.findById(id);
    }
    
    public Squad saveSquad(Squad squad) {
        return squadRepository.save(squad);
    }
    
    public void deleteSquad(Long id) {
        squadRepository.deleteById(id);
    }
    
    public Map<String, Object> optimizeSquad(Double budget) {
        // Get all players with predictions
        List<Map<String, Object>> players = fplApiService.getAllPlayers();
        Map<String, Double> predictions = mlServiceClient.getPredictions(players);
        
        // Add predictions to players
        players.forEach(player -> {
            Integer playerId = (Integer) player.get("id");
            player.put("predicted_points", predictions.getOrDefault(String.valueOf(playerId), 0.0));
        });
        
        // Call ML service for optimization
        return mlServiceClient.optimizeSquad(players, budget);
    }
}
```

## Phase 7: Deployment (100% Free on Render.com)

**All services deployed on Render.com for simplicity**

### Step 1: Create PostgreSQL Database

1. Go to render.com → Dashboard → New → PostgreSQL
2. Name: `fpl-database`
3. Region: Choose closest to you
4. Plan: Free (1GB storage, 90-day expiry)
5. Click "Create Database"
6. Copy the **Internal Database URL** (for services on Render) and **External Database URL** (for local dev)

**Note:** Free tier expires after 90 days but you can recreate it. Data can be backed up before expiry.

---

### Step 2: Deploy Flask ML Service

1. Push `ml-service` folder to GitHub (can be same repo or separate)
2. Go to Render → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - **Name:** `fpl-ml-service`
   - **Root Directory:** `ml-service` (if in same repo)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Add `gunicorn` to `requirements.txt`:
   ```
   gunicorn
   ```
6. Deploy

**Note the URL:** `https://fpl-ml-service.onrender.com`

---

### Step 3: Deploy Spring Boot Backend

1. Create `Dockerfile` in `/backend`:

```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

2. Push backend to GitHub
3. Go to Render → New → Web Service
4. Connect your GitHub repo
5. Settings:
   - **Name:** `fpl-backend`
   - **Root Directory:** `backend` (if in same repo)
   - **Runtime:** Docker
   - **Instance Type:** Free
6. Add Environment Variables:
   - `SPRING_DATASOURCE_URL` = (Internal Database URL from Step 1)
   - `SPRING_DATASOURCE_USERNAME` = (from Render PostgreSQL)
   - `SPRING_DATASOURCE_PASSWORD` = (from Render PostgreSQL)
   - `ML_SERVICE_URL` = `https://fpl-ml-service.onrender.com`
7. Deploy

**Note the URL:** `https://fpl-backend.onrender.com`

---

### Step 4: Deploy React Frontend

1. Add build script to `package.json`:
   ```json
   "scripts": {
     "build": "react-scripts build"
   }
   ```

2. Create `.env.production` in frontend:
   ```
   REACT_APP_API_URL=https://fpl-backend.onrender.com
   ```

3. Push frontend to GitHub
4. Go to Render → New → Static Site
5. Connect your GitHub repo
6. Settings:
   - **Name:** `fpl-frontend`
   - **Root Directory:** `frontend` (if in same repo)
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `build`
7. Add Environment Variable:
   - `REACT_APP_API_URL` = `https://fpl-backend.onrender.com`
8. Deploy

**Final URL:** `https://fpl-frontend.onrender.com`

---

### Render.com Free Tier Limits

| Service | Free Tier Limit |
|---------|-----------------|
| **Static Sites** | Unlimited bandwidth, 100 GB/month |
| **Web Services** | 750 hours/month total (shared across all services) |
| **PostgreSQL** | 1GB storage, 90-day expiry (can recreate) |

**Important Notes:**
- Free web services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- 750 hours/month is shared across ALL your free web services
- With 2 web services (backend + ML), you get ~15 hours/day each (enough for personal project)

---

### Project Structure for Single Repo Deployment

```
/fpl
├── /backend              # Spring Boot (Render Web Service)
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
├── /ml-service           # Flask ML (Render Web Service)
│   ├── requirements.txt
│   ├── app.py
│   └── ...
├── /frontend             # React (Render Static Site)
│   ├── package.json
│   ├── .env.production
│   └── src/
├── plan.md
└── README.md
```

Each folder is deployed as a separate Render service with its own root directory setting.

## Implementation Order (Step-by-Step)

1. **Spring Boot backend setup** - Create project, configure PostgreSQL
2. **React frontend setup** - Create React app, basic routing
3. **FPL API integration** - Service class in Spring Boot
4. **Display players** - Fetch and display in React
5. **Flask ML service setup** - Basic Flask app
6. **Data processing** - Download Vaastav data, preprocessing
7. **Train baseline model** - Linear Regression
8. **Prediction API** - Flask endpoint, Spring Boot calls it via RestTemplate
9. **Show predictions in React** - Display predicted points
10. **Train advanced models** - Neural Net, Random Forest
11. **Optimization engine** - PuLP implementation
12. **SquadBuilder UI** - Full team planner
13. **PostgreSQL integration** - Save/load squads with JPA
14. **Polish & deploy** - Styling, deployment


