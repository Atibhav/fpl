# FPL ML Team Builder - Development Documentation

This document serves as a comprehensive development guide and tutorial for building the FPL ML Team Builder project. It documents every step of the development process, including code written, concepts explained, issues encountered, and their resolutions.

**Target Audience:** Junior developers learning full-stack development with Java/Spring Boot, React, Flask, and Machine Learning.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Development Steps](#development-steps)
   - [Step 1: Spring Boot Backend Setup](#step-1-spring-boot-backend-setup)
   - [Step 2: React Frontend Setup](#step-2-react-frontend-setup)
   - [Step 3: Connecting Frontend to Backend](#step-3-connecting-frontend-to-backend)
   - [Step 4: FPL API Integration](#step-4-fpl-api-integration)
   - [Step 5: Flask ML Service Setup](#step-5-flask-ml-service-setup)
   - [Step 6: Data Pipeline](#step-6-data-pipeline)
   - [Step 7: ML Models](#step-7-ml-models)
   - [Step 8: Optimization Engine](#step-8-optimization-engine)
   - [Step 9: Full UI Implementation](#step-9-full-ui-implementation)
   - [Step 10: Database Integration](#step-10-database-integration)
   - [Step 11: Deployment](#step-11-deployment)
6. [Issues and Resolutions](#issues-and-resolutions)
7. [Key Concepts Explained](#key-concepts-explained)

---

## Project Overview

The FPL ML Team Builder is a full-stack web application that helps Fantasy Premier League managers:

1. **Predict player points** using machine learning models trained on historical data
2. **Optimize squad selection** using linear programming to find the best team within budget constraints
3. **Plan transfers** with an interactive team builder interface
4. **Analyze fixtures** to make informed decisions about upcoming gameweeks

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React (JavaScript) | User interface, components, state management |
| **Backend API** | Java + Spring Boot | REST API, business logic, external API calls |
| **ML Service** | Python + Flask | Machine learning predictions, optimization |
| **Database** | PostgreSQL | Storing saved squads (added later) |
| **Styling** | Vanilla CSS (Flexbox/Grid) | Learning CSS fundamentals |

### Why This Stack?

- **Spring Boot**: Enterprise-grade Java framework, widely used in industry, great for SDE resume
- **React**: Most popular frontend framework, component-based architecture
- **Flask**: Lightweight Python web framework, perfect for ML model serving
- **PostgreSQL**: Industry-standard relational database, works great with Spring Data JPA

---

## Prerequisites

Before starting development, ensure you have installed:

1. **Java 17 or higher** (JDK)
   ```bash
   # Install on Ubuntu/WSL
   sudo apt update
   sudo apt install openjdk-17-jdk -y
   
   # Verify installation
   java -version
   ```

2. **Node.js and npm** (for React)
   ```bash
   # Install Node.js (v18+ recommended)
   # Download from https://nodejs.org or use nvm
   
   # Verify installation
   node -v
   npm -v
   ```

3. **Python 3.10+** (for Flask ML service)
   ```bash
   python3 --version
   pip3 --version
   ```

4. **Git** (version control)
   ```bash
   git --version
   ```

5. **Maven** (comes with Spring Boot wrapper, but good to have)

---

## Project Structure

```
fpl/
├── server/                 # Spring Boot backend (Java)
│   ├── pom.xml            # Maven dependencies
│   ├── mvnw               # Maven wrapper script
│   └── src/
│       └── main/
│           ├── java/com/fpl/server/
│           │   ├── ServerApplication.java      # Main entry point
│           │   ├── controller/                 # REST controllers
│           │   │   └── HealthController.java
│           │   ├── service/                    # Business logic
│           │   ├── model/                      # JPA entities
│           │   └── repository/                 # Data access
│           └── resources/
│               └── application.properties      # Configuration
│
├── client/                 # React frontend
│   ├── package.json
│   └── src/
│       ├── App.js
│       ├── index.js
│       ├── components/     # Reusable UI components
│       ├── pages/          # Route pages
│       ├── services/       # API calls
│       └── styles/         # CSS files
│
├── ml-service/             # Flask ML backend (Python)
│   ├── app.py
│   ├── requirements.txt
│   ├── ml/                 # ML models
│   ├── optimization/       # PuLP optimization
│   └── data/               # Data processing
│
├── plan.md                 # Project plan
├── DEVELOPMENT.md          # This file - development documentation
└── README.md               # Project overview
```

---

## Development Steps

---

# Step 1: Spring Boot Backend Setup

**Goal:** Create a Spring Boot application with a simple health check endpoint to verify the server is running.

## 1.1 Create the Spring Boot Project

We used [Spring Initializr](https://start.spring.io/) to generate the project with these settings:

| Setting | Value |
|---------|-------|
| Project | Maven |
| Language | Java |
| Spring Boot | 3.4.12 |
| Group | com.fpl |
| Artifact | server |
| Packaging | Jar |
| Java | 17 |

**Dependencies added:**
- Spring Web (for REST APIs)
- Spring Data JPA (for database access)
- PostgreSQL Driver (database driver)
- Lombok (reduces boilerplate code)
- Validation (input validation)

### How to Create:

1. Go to https://start.spring.io/
2. Fill in the settings above
3. Click "Add Dependencies" and add the dependencies listed
4. Click "Generate" to download the zip file
5. Extract to your project's `server/` folder

### Terminal Commands:

```bash
# Navigate to project root
cd /home/atibhav/repos/fpl

# Create project folders
mkdir -p server client ml-service

# After downloading server.zip from Spring Initializr:
mv ~/Downloads/server.zip .
unzip server.zip
rm server.zip

# Verify structure
ls server/
# Output: HELP.md  mvnw  mvnw.cmd  pom.xml  src
```

---

## 1.2 Configure Application Properties

The `application.properties` file configures how Spring Boot runs.

**File:** `server/src/main/resources/application.properties`

```properties
spring.application.name=server

# Server port
server.port=8080

# Temporarily disable database auto-configuration (we'll enable it later)
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration

# ML Service URL (Flask)
ml.service.url=http://localhost:5001

# FPL API URL
fpl.api.base-url=https://fantasy.premierleague.com/api
```

### Explanation:

- `server.port=8080`: The server will run on http://localhost:8080
- `spring.autoconfigure.exclude=...`: This tells Spring Boot NOT to automatically configure the database. We do this because:
  - We haven't set up PostgreSQL yet
  - Without this, Spring Boot would fail to start because it can't connect to a database
  - We'll remove this line later when we add the database

---

## 1.3 Create the Health Controller

A **Controller** in Spring Boot is a class that handles HTTP requests. Our first controller will handle requests to `/api/health`.

**File:** `server/src/main/java/com/fpl/server/controller/HealthController.java`

```java
package com.fpl.server.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * Health Controller - Simple endpoint to verify the server is running.
 * 
 * This is our first REST controller! Here's what each annotation does:
 * 
 * @RestController - Tells Spring this class handles HTTP requests and 
 *                   automatically converts return values to JSON.
 * 
 * @RequestMapping("/api") - All endpoints in this controller start with /api
 * 
 * @GetMapping("/health") - This method handles GET requests to /api/health
 */
@RestController
@RequestMapping("/api")
public class HealthController {

    /**
     * GET /api/health
     * 
     * Returns a simple JSON response to confirm the server is running.
     * 
     * ResponseEntity is a Spring class that lets us control:
     * - The HTTP status code (200 OK, 404 Not Found, etc.)
     * - The response body (our JSON data)
     * - Response headers if needed
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "ok");
        response.put("message", "FPL ML Team Builder API is running!");
        
        return ResponseEntity.ok(response);
    }
}
```

### Key Concepts:

#### Annotations Explained:

| Annotation | Purpose |
|------------|---------|
| `@RestController` | Marks this class as a REST API controller. Combines `@Controller` + `@ResponseBody`, meaning return values are automatically converted to JSON. |
| `@RequestMapping("/api")` | Sets the base URL path for all endpoints in this class. All methods will have URLs starting with `/api`. |
| `@GetMapping("/health")` | Maps HTTP GET requests to `/api/health` to this method. There's also `@PostMapping`, `@PutMapping`, `@DeleteMapping` for other HTTP methods. |

#### ResponseEntity:

`ResponseEntity<T>` is a wrapper class that gives you control over the HTTP response:

```java
// Return 200 OK with body
return ResponseEntity.ok(data);

// Return 201 Created
return ResponseEntity.status(HttpStatus.CREATED).body(data);

// Return 404 Not Found
return ResponseEntity.notFound().build();

// Return 500 Internal Server Error
return ResponseEntity.internalServerError().body(error);
```

---

## 1.4 Run the Spring Boot Application

### First Run (Downloads Dependencies):

```bash
cd /home/atibhav/repos/fpl/server
./mvnw spring-boot:run
```

**What happens:**
1. Maven downloads all dependencies (first time takes 2-5 minutes)
2. Spring Boot compiles your Java code
3. Embedded Tomcat server starts on port 8080

### Expected Output:

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::               (v3.4.12)

2025-12-02T23:14:55.519+05:30  INFO 44942 --- [server] [main] com.fpl.server.ServerApplication : Started ServerApplication in X.XXX seconds
```

### Test the Endpoint:

Open your browser and go to:
```
http://localhost:8080/api/health
```

**Expected Response:**
```json
{"message":"FPL ML Team Builder API is running!","status":"ok"}
```

### What About the Root URL?

If you go to `http://localhost:8080/` (without `/api/health`), you'll see:

```
Whitelabel Error Page
This application has no explicit mapping for /error, so you are seeing this as a fallback.
There was an unexpected error (type=Not Found, status=404).
```

This is **expected and correct**! We haven't created an endpoint for `/`, only for `/api/health`.

---

## 1.5 Project Structure After Step 1

```
server/
├── pom.xml
├── mvnw
├── mvnw.cmd
├── HELP.md
└── src/
    └── main/
        ├── java/
        │   └── com/
        │       └── fpl/
        │           └── server/
        │               ├── ServerApplication.java    # Main entry point (auto-generated)
        │               └── controller/
        │                   └── HealthController.java # Our first controller
        └── resources/
            └── application.properties                # Configuration
```

---

# Step 2: React Frontend Setup

**Goal:** Create a React application that will eventually call our Spring Boot backend.

## 2.1 Create the React App

We use Create React App (CRA) to bootstrap our React project.

### Terminal Commands:

```bash
cd /home/atibhav/repos/fpl/client
npx create-react-app . --template cra-template
```

**Explanation:**
- `npx` - Runs npm packages without installing them globally
- `create-react-app` - The CLI tool that creates React projects
- `.` - Create in the current directory (client/)
- `--template cra-template` - Use the default template

**Note:** You might see a deprecation warning about create-react-app. This is fine for learning purposes.

### Installation Output:

```
Creating a new React app in /home/atibhav/repos/fpl/client.
Installing packages. This might take a couple of minutes.
Installing react, react-dom, and react-scripts with cra-template...

added 1312 packages in 54s

Success! Created client at /home/atibhav/repos/fpl/client
```

---

## 2.2 Run the React Development Server

```bash
cd /home/atibhav/repos/fpl/client
npm start
```

This starts the development server on `http://localhost:3000`. You should see the React logo spinning in your browser.

---

## 2.3 Understanding the Default React Structure

After running create-react-app, you get:

```
client/
├── node_modules/          # Dependencies (don't touch)
├── public/
│   ├── index.html         # HTML template
│   └── favicon.ico        # Browser tab icon
├── src/
│   ├── App.js             # Main component
│   ├── App.css            # Styles for App
│   ├── App.test.js        # Tests (we'll skip for now)
│   ├── index.js           # Entry point - renders App
│   ├── index.css          # Global styles
│   ├── logo.svg           # React logo (we'll delete)
│   ├── reportWebVitals.js # Performance (we'll skip)
│   └── setupTests.js      # Test setup (we'll skip)
├── package.json           # Project config and dependencies
└── package-lock.json      # Locked dependency versions
```

### Key Files Explained:

**`src/index.js`** - The entry point. React renders the App component into the DOM:

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**`src/App.js`** - The main component (currently shows the spinning logo):

```javascript
import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
```

---

## 2.4 Clean Up and Organize

We'll organize our React app into a proper structure. First, create the folders:

```bash
mkdir -p src/services src/pages src/components src/styles
```

**Folder purposes:**
- `services/` - API calls to the backend
- `pages/` - Full page components (Home, Planner, etc.)
- `components/` - Reusable UI pieces (PlayerCard, PitchView, etc.)
- `styles/` - CSS files

---

## 2.5 Create the API Service

This file will handle all API calls to our Spring Boot backend. We use the native `fetch` API instead of axios to keep dependencies minimal.

**File:** `client/src/services/api.js`

```javascript
/**
 * API Service
 * 
 * This file contains all the functions that communicate with our backend.
 * We use the native fetch API (no external libraries needed).
 * 
 * For now, we only have the health check endpoint.
 * We'll add more endpoints as we build out the backend.
 */

// Base URL for our Spring Boot backend
// In development, this is localhost:8080
// In production, this would be the deployed URL
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

/**
 * Check if the backend server is running
 * 
 * @returns {Promise<Object>} - { status: "ok", message: "..." }
 */
export const getHealth = async () => {
  try {
    const response = await fetch(`${API_BASE}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling health endpoint:', error);
    throw error;
  }
};

/**
 * Get all players with predicted points
 * This will call GET /api/players
 * 
 * @returns {Promise<Array>} - Array of player objects
 */
export const getPlayers = async () => {
  try {
    const response = await fetch(`${API_BASE}/players`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching players:', error);
    throw error;
  }
};

/**
 * Optimize squad selection
 * This will call POST /api/squads/optimize
 * 
 * @param {number} budget - Maximum budget for the squad
 * @returns {Promise<Object>} - Optimized squad with total cost and expected points
 */
export const optimizeSquad = async (budget) => {
  try {
    const response = await fetch(`${API_BASE}/squads/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ budget }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error optimizing squad:', error);
    throw error;
  }
};

/**
 * Save a squad to the database
 * This will call POST /api/squads
 * 
 * @param {Object} squad - Squad object to save
 * @returns {Promise<Object>} - Saved squad with ID
 */
export const saveSquad = async (squad) => {
  try {
    const response = await fetch(`${API_BASE}/squads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(squad),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving squad:', error);
    throw error;
  }
};

/**
 * Get all saved squads
 * This will call GET /api/squads
 * 
 * @returns {Promise<Array>} - Array of saved squad objects
 */
export const getSavedSquads = async () => {
  try {
    const response = await fetch(`${API_BASE}/squads`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching saved squads:', error);
    throw error;
  }
};
```

### Key Concepts:

#### `fetch` API:
The native browser API for making HTTP requests. Returns a Promise.

```javascript
// Basic usage
const response = await fetch(url);           // Make request
const data = await response.json();          // Parse JSON response

// POST request with body
const response = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: 'value' })
});
```

#### Environment Variables:
`process.env.REACT_APP_API_URL` reads from environment variables. In React, env vars must start with `REACT_APP_`.

---

## 2.6 Update App.js to Call the Backend

Replace the default App.js with our custom version that calls the health endpoint.

**File:** `client/src/App.js`

```javascript
import React, { useState, useEffect } from 'react';
import { getHealth } from './services/api';
import './App.css';

/**
 * Main App Component
 * 
 * This is the root component of our React application.
 * 
 * Concepts used:
 * - useState: React hook for managing component state
 * - useEffect: React hook for side effects (API calls, etc.)
 */
function App() {
  // State variables
  // useState returns [currentValue, setterFunction]
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // useEffect runs after component mounts (and when dependencies change)
  // Empty dependency array [] means it runs once when component first loads
  useEffect(() => {
    checkBackendHealth();
  }, []);

  /**
   * Call the backend health endpoint
   */
  const checkBackendHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await getHealth();
      setHealthStatus(data);
    } catch (err) {
      setError('Failed to connect to backend. Is the server running on port 8080?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>FPL ML Team Builder</h1>
        
        <div className="status-box">
          <h2>Backend Status:</h2>
          
          {loading && <p className="loading">Checking connection...</p>}
          
          {error && (
            <div className="error">
              <p>❌ {error}</p>
              <button onClick={checkBackendHealth}>Retry</button>
            </div>
          )}
          
          {healthStatus && (
            <div className="success">
              <p>✅ Status: {healthStatus.status}</p>
              <p>📝 {healthStatus.message}</p>
            </div>
          )}
        </div>

        <p className="info">
          This page demonstrates the React frontend communicating 
          with the Spring Boot backend.
        </p>
      </header>
    </div>
  );
}

export default App;
```

### Key React Concepts:

#### `useState` Hook:
Manages state within a component. State changes trigger re-renders.

```javascript
const [value, setValue] = useState(initialValue);

// Reading state
console.log(value);

// Updating state
setValue(newValue);
```

#### `useEffect` Hook:
Runs side effects (API calls, subscriptions, timers).

```javascript
// Runs once on mount (like componentDidMount)
useEffect(() => {
  // Do something
}, []);

// Runs when `dependency` changes
useEffect(() => {
  // Do something when dependency updates
}, [dependency]);

// Cleanup function (like componentWillUnmount)
useEffect(() => {
  const timer = setInterval(...);
  return () => clearInterval(timer);  // Cleanup
}, []);
```

---

## 2.7 Update the CSS

**File:** `client/src/App.css`

```css
/**
 * App Styles
 * 
 * These styles use Flexbox for centering content.
 * We're using a dark theme with FPL-inspired colors.
 * 
 * CSS Concepts Used:
 * - Flexbox: For layout and centering
 * - CSS Variables: For consistent colors (we'll add more later)
 * - Box model: padding, margin, border-radius
 * - Responsive units: rem, vh
 */

/* ============================================
   RESET & BASE STYLES
   ============================================ */

/* Box-sizing: border-box makes width/height include padding and border */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base app container */
.App {
  text-align: center;
  min-height: 100vh;
  background-color: #1a1a2e;
  color: #eee;
}

/* ============================================
   HEADER / MAIN CONTENT
   ============================================ */

/* 
 * Flexbox Centering Explained:
 * 
 * display: flex       - Makes this a flex container
 * flex-direction: column - Stack children vertically (default is row/horizontal)
 * align-items: center - Center items on the cross axis (horizontal when direction is column)
 * justify-content: center - Center items on the main axis (vertical when direction is column)
 * min-height: 100vh   - At least full viewport height
 */
.App-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

/* Main title - FPL green color */
h1 {
  font-size: 2.5rem;
  margin-bottom: 30px;
  color: #00ff87; /* FPL's signature green */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ============================================
   STATUS BOX COMPONENT
   ============================================ */

.status-box {
  background-color: #16213e;
  border-radius: 10px;
  padding: 30px;
  margin: 20px 0;
  min-width: 300px;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.status-box h2 {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: #aaa;
  font-weight: normal;
}

/* ============================================
   STATE STYLES (Loading, Error, Success)
   ============================================ */

.loading {
  color: #ffc107; /* Warning yellow */
  font-style: italic;
}

.error {
  color: #ff5252; /* Error red */
}

.error p {
  margin-bottom: 10px;
}

.error button {
  padding: 8px 20px;
  background-color: #ff5252;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s ease;
}

.error button:hover {
  background-color: #ff1744;
}

.success {
  color: #00ff87; /* FPL green */
}

.success p {
  margin: 8px 0;
  font-size: 1.1rem;
}

/* ============================================
   INFO TEXT
   ============================================ */

.info {
  margin-top: 30px;
  color: #888;
  max-width: 400px;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* ============================================
   UTILITY CLASSES (for future use)
   ============================================ */

.text-center {
  text-align: center;
}

.mt-20 {
  margin-top: 20px;
}

.mb-20 {
  margin-bottom: 20px;
}
```

### CSS Concepts Explained:

#### Box Model:
Every element is a box with content, padding, border, and margin.
```css
box-sizing: border-box; /* Padding included in width/height */
```

#### Flexbox:
Modern CSS layout system for one-dimensional layouts.

```css
.container {
  display: flex;              /* Enable flexbox */
  flex-direction: column;     /* Stack vertically (row is horizontal) */
  justify-content: center;    /* Main axis alignment */
  align-items: center;        /* Cross axis alignment */
  gap: 10px;                  /* Space between flex items */
}
```

---

## 2.8 Test the Frontend-Backend Connection

### Start Both Servers:

**Terminal 1 - Spring Boot Backend:**
```bash
cd /home/atibhav/repos/fpl/server
./mvnw spring-boot:run
```

**Terminal 2 - React Frontend:**
```bash
cd /home/atibhav/repos/fpl/client
npm start
```

### Expected Result:

Open `http://localhost:3000` in your browser. You should see:

- "FPL ML Team Builder" heading
- "Backend Status:" section
- If backend is running: ✅ Status: ok, 📝 FPL ML Team Builder API is running!
- If backend is not running: ❌ Failed to connect to backend. Is the server running?

---

# Issues and Resolutions

## Issue 1: Spring Boot Download Failed with curl

**Problem:**
When downloading Spring Initializr project with curl, the zip file was corrupted (only 194 bytes instead of ~60KB).

**Symptoms:**
```bash
$ unzip server.zip
Archive:  server.zip
End-of-central-directory signature not found.
```

**Resolution:**
Downloaded the project manually via browser instead:
1. Go to https://start.spring.io/
2. Configure settings and dependencies
3. Click "Generate" to download
4. Move zip file to project folder and extract

**Why it happened:**
The curl command wasn't following redirects properly, or there was a network issue with the Spring Initializr API.

---

## Issue 2: JAVA_HOME Not Set

**Problem:**
```
The JAVA_HOME environment variable is not defined correctly,
this environment variable is needed to run this program.
```

**Resolution:**
Install Java JDK and set JAVA_HOME:

```bash
# Install Java 17
sudo apt update
sudo apt install openjdk-17-jdk -y

# Verify
java -version
```

The Maven wrapper (`mvnw`) automatically finds Java after installation.

---

## Issue 3: Database Connection Error

**Problem:**
```
Failed to configure a DataSource: 'url' attribute is not specified
Failed to determine a suitable driver class
```

**Why it happened:**
We added Spring Data JPA and PostgreSQL Driver as dependencies, so Spring Boot automatically tried to configure a database connection, but we hadn't set up PostgreSQL yet.

**Resolution:**
Temporarily disable database auto-configuration in `application.properties`:

```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration
```

We'll remove this line later when we add PostgreSQL.

---

## Issue 4: 404 Error on Root URL

**Problem:**
Visiting `http://localhost:8080/` shows "Whitelabel Error Page" with 404 status.

**Explanation:**
This is **not actually an error**! We created an endpoint at `/api/health`, not at `/`. The 404 simply means there's no handler for the root URL.

**Resolution:**
Visit the correct URL: `http://localhost:8080/api/health`

---

# Key Concepts Explained

## REST API Architecture

REST (Representational State Transfer) is an architectural style for web services.

**Key Principles:**
- **Resources** are identified by URLs (`/api/players`, `/api/squads`)
- **HTTP Methods** define operations:
  - `GET` - Read data
  - `POST` - Create data
  - `PUT` - Update data
  - `DELETE` - Remove data
- **JSON** is used for data exchange

**Example:**
```
GET /api/players        → Get all players
GET /api/players/123    → Get player with ID 123
POST /api/squads        → Create new squad
DELETE /api/squads/456  → Delete squad with ID 456
```

---

## Spring Boot Annotations Cheat Sheet

| Annotation | Purpose |
|------------|---------|
| `@RestController` | Marks class as REST API controller, returns JSON |
| `@RequestMapping("/api")` | Base URL path for controller |
| `@GetMapping("/path")` | Handle GET requests |
| `@PostMapping("/path")` | Handle POST requests |
| `@PutMapping("/path")` | Handle PUT requests |
| `@DeleteMapping("/path")` | Handle DELETE requests |
| `@PathVariable` | Extract value from URL path |
| `@RequestBody` | Parse JSON body into object |
| `@RequestParam` | Get query parameter |
| `@Autowired` | Dependency injection |
| `@Service` | Business logic class |
| `@Repository` | Data access class |
| `@Entity` | JPA database entity |

---

## React Hooks Cheat Sheet

| Hook | Purpose |
|------|---------|
| `useState` | Manage component state |
| `useEffect` | Side effects (API calls, subscriptions) |
| `useContext` | Access context values |
| `useRef` | Persist values across renders |
| `useMemo` | Memoize expensive calculations |
| `useCallback` | Memoize functions |

---

## CSS Flexbox Quick Reference

```css
.container {
  display: flex;
  
  /* Direction */
  flex-direction: row;      /* horizontal (default) */
  flex-direction: column;   /* vertical */
  
  /* Main Axis (direction of items) */
  justify-content: flex-start;   /* start */
  justify-content: center;       /* center */
  justify-content: flex-end;     /* end */
  justify-content: space-between; /* spread out */
  justify-content: space-around;  /* spread with margins */
  
  /* Cross Axis (perpendicular) */
  align-items: stretch;     /* fill height (default) */
  align-items: center;      /* center */
  align-items: flex-start;  /* top */
  align-items: flex-end;    /* bottom */
  
  /* Wrapping */
  flex-wrap: nowrap;        /* single line (default) */
  flex-wrap: wrap;          /* multiple lines */
  
  /* Gap between items */
  gap: 10px;
}

.item {
  flex: 1;                  /* grow to fill space */
  flex: 0 0 200px;          /* fixed 200px width */
}
```

---

# Step 3: Connecting Frontend to Backend (CORS Configuration)

**Goal:** Make the React frontend successfully communicate with the Spring Boot backend.

## 3.1 Understanding CORS

When you run React on `http://localhost:3000` and try to call Spring Boot on `http://localhost:8080`, the browser blocks the request due to **CORS (Cross-Origin Resource Sharing)** policy.

### What is CORS?

CORS is a browser security feature that prevents web pages from making requests to a different domain/port than the one that served the page.

- **Same Origin:** `http://localhost:3000` calling `http://localhost:3000` → ✅ Allowed
- **Different Origin:** `http://localhost:3000` calling `http://localhost:8080` → ❌ Blocked by default

### How to Fix CORS?

The **server** (Spring Boot) needs to tell the browser "it's okay to accept requests from this frontend."

We already added a `CorsConfig.java` file in Step 1, but let's verify it's correct.

## 3.2 CORS Configuration in Spring Boot

**File:** `server/src/main/java/com/fpl/server/config/CorsConfig.java`

```java
package com.fpl.server.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * CORS Configuration
 * 
 * This class configures Cross-Origin Resource Sharing (CORS) for our API.
 * 
 * Why do we need this?
 * - React runs on localhost:3000
 * - Spring Boot runs on localhost:8080
 * - Browsers block cross-origin requests by default (security feature)
 * - This config tells the browser "it's okay to accept requests from localhost:3000"
 */
@Configuration
public class CorsConfig {
    
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                        .allowedOrigins(
                            "http://localhost:3000",           // React dev server
                            "http://127.0.0.1:3000",           // Alternative localhost
                            "https://fpl-frontend.onrender.com" // Production (update later)
                        )
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        .allowedHeaders("*")
                        .allowCredentials(true);
            }
        };
    }
}
```

### Key Concepts:

| Method | Purpose |
|--------|---------|
| `addMapping("/api/**")` | Apply CORS to all endpoints starting with `/api/` |
| `allowedOrigins(...)` | List of allowed frontend URLs |
| `allowedMethods(...)` | HTTP methods the frontend can use |
| `allowedHeaders("*")` | Allow all request headers |
| `allowCredentials(true)` | Allow cookies and authentication headers |

---

## 3.3 Create the CORS Config File

Let's create this file in the Spring Boot project:

**Terminal Commands:**

```bash
mkdir -p /home/atibhav/repos/fpl/server/src/main/java/com/fpl/server/config
```

Then create the file with the content shown above.

---

## 3.4 Test the Frontend-Backend Connection

### Step 1: Start the Spring Boot Backend

```bash
cd /home/atibhav/repos/fpl/server
./mvnw spring-boot:run
```

Wait until you see: `Started ServerApplication in X.XXX seconds`

### Step 2: Start the React Frontend (in a new terminal)

```bash
cd /home/atibhav/repos/fpl/client
npm start
```

### Step 3: Open Browser

Go to `http://localhost:3000`

You should see:
- "FPL ML Team Builder" heading
- **"Backend Status:"** section with ✅ Status: ok

If you see an error instead, check:
1. Is the Spring Boot server running on port 8080?
2. Is there a CORS error in the browser console (F12 → Console)?

---

## 3.5 Project Structure After Step 3

```
fpl/
├── server/
│   └── src/main/java/com/fpl/server/
│       ├── ServerApplication.java
│       ├── controller/
│       │   └── HealthController.java
│       └── config/
│           └── CorsConfig.java          # NEW: CORS configuration
│
├── client/
│   └── src/
│       ├── App.js                       # UPDATED: Calls backend
│       ├── App.css                      # UPDATED: Custom styles
│       └── services/
│           └── api.js                   # NEW: API service
│
├── ml-service/                          # Empty for now
├── plan.md
└── DEVELOPMENT.md                       # This file
```

---

# Next Steps

After completing Steps 1-3, we have:
- ✅ Spring Boot backend with `/api/health` endpoint
- ✅ React frontend that calls the backend
- ✅ CORS configured for cross-origin requests
- ✅ Basic project structure

**Coming up:**
- Step 4: FPL API Integration in Spring Boot
- Step 5: Display player data in React
- Step 6: Flask ML service setup
- And more...

---

*This documentation is updated as development progresses. Last updated: December 2, 2025*

---

# Progress Summary

## Completed Steps ✅

| Step | Description | Status |
|------|-------------|--------|
| 1 | Spring Boot backend with `/api/health` | ✅ Complete |
| 2 | React frontend setup | ✅ Complete |
| 3 | Frontend-Backend connection (CORS) | ✅ Complete |
| 4 | FPL API Integration (players, teams, fixtures) | ✅ Complete |
| 5 | Display Players in React (with filters & sorting) | ✅ Complete |

## Current Project Structure

```
fpl/
├── server/                              # Spring Boot backend
│   ├── pom.xml
│   ├── mvnw
│   └── src/main/java/com/fpl/server/
│       ├── ServerApplication.java
│       ├── controller/
│       │   ├── HealthController.java
│       │   └── PlayerController.java   # FPL data endpoints
│       ├── service/
│       │   ├── FplApiService.java      # FPL API integration with caching
│       │   └── PlayerService.java      # Player data enrichment
│       └── config/
│           └── CorsConfig.java
│
├── client/                              # React frontend
│   ├── package.json
│   └── src/
│       ├── App.js                       # Routing & navigation
│       ├── App.css
│       ├── services/
│       │   └── api.js                   # API calls to backend
│       ├── components/
│       │   ├── PlayerCard.js            # Player card component
│       │   └── PlayerCard.css
│       ├── pages/
│       │   ├── PlayersPage.js           # Players list with filters
│       │   └── PlayersPage.css
│       └── styles/
│
├── ml-service/                          # Flask ML service (next step)
│
├── plan.md                              # Project plan
├── DEVELOPMENT.md                       # This file
└── README.md
```

## Next Up

**Step 6: Flask ML Service Setup** - Initialize the Python Flask service for machine learning predictions.

---

# Step 4: FPL API Integration

**Goal:** Fetch real player data from the official Fantasy Premier League API and expose it through our Spring Boot backend.

## 4.1 Understanding the FPL API

The official FPL API is **free and public** — no authentication required!

### Key Endpoints:

| Endpoint | Description | Data |
|----------|-------------|------|
| `/bootstrap-static/` | All static data | Players, teams, gameweeks, positions |
| `/fixtures/` | All fixtures | Match schedule with difficulty ratings |
| `/entry/{team_id}/` | User's team info | Team name, overall rank, points |
| `/entry/{team_id}/event/{gw}/picks/` | User's picks for a gameweek | Selected players, captain, bench |

### Example Response (bootstrap-static):

The main endpoint returns a large JSON object with:
- `elements`: Array of all 650+ players with stats
- `teams`: Array of all 20 Premier League teams
- `element_types`: Array of positions (GK, DEF, MID, FWD)
- `events`: Array of all 38 gameweeks

## 4.2 Create the FPL API Service

This service handles all communication with the FPL API and includes caching to avoid hitting the API too frequently.

**File:** `server/src/main/java/com/fpl/server/service/FplApiService.java`

```java
package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * FPL API Service
 * 
 * Handles all communication with the official Fantasy Premier League API.
 * Includes a simple in-memory cache to avoid hitting the API too frequently.
 * 
 * Key Concepts:
 * - @Service: Marks this as a Spring service (business logic layer)
 * - @Value: Injects values from application.properties
 * - RestTemplate: Spring's HTTP client for making API calls
 * - ConcurrentHashMap: Thread-safe cache for storing API responses
 */
@Service
public class FplApiService {
    
    // Inject the FPL API base URL from application.properties
    @Value("${fpl.api.base-url}")
    private String fplBaseUrl;
    
    // RestTemplate is Spring's HTTP client - simpler than using HttpClient directly
    private final RestTemplate restTemplate = new RestTemplate();
    
    // Simple in-memory cache using ConcurrentHashMap (thread-safe)
    private final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();
    
    // Cache duration: 5 minutes (FPL data doesn't change that frequently)
    private static final long CACHE_DURATION_MS = 5 * 60 * 1000;
    
    /**
     * Inner class to hold cached data with timestamp
     */
    private static class CacheEntry {
        Object data;
        long timestamp;
        
        CacheEntry(Object data) {
            this.data = data;
            this.timestamp = System.currentTimeMillis();
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() - timestamp > CACHE_DURATION_MS;
        }
    }
    
    /**
     * Fetch the main bootstrap data (all players, teams, gameweeks)
     * This is cached because it's a large response (~2MB) and doesn't change often
     */
    @SuppressWarnings("unchecked")  // Suppress warnings about generic type casting
    public Map<String, Object> getBootstrapData() {
        String cacheKey = "bootstrap";
        
        // Check cache first
        CacheEntry entry = cache.get(cacheKey);
        if (entry != null && !entry.isExpired()) {
            return (Map<String, Object>) entry.data;
        }
        
        // Cache miss or expired - fetch from API
        String url = fplBaseUrl + "/bootstrap-static/";
        Map<String, Object> response = restTemplate.getForObject(url, Map.class);
        
        // Store in cache
        if (response != null) {
            cache.put(cacheKey, new CacheEntry(response));
        }
        
        return response;
    }
    
    /**
     * Get all players from the bootstrap data
     * Returns the "elements" array which contains 650+ player objects
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getAllPlayers() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("elements");
    }
    
    /**
     * Get all Premier League teams
     * Returns the "teams" array (20 teams)
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getAllTeams() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("teams");
    }
    
    /**
     * Get position types (GK, DEF, MID, FWD)
     * Returns the "element_types" array
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getElementTypes() {
        Map<String, Object> bootstrap = getBootstrapData();
        return (List<Map<String, Object>>) bootstrap.get("element_types");
    }
    
    /**
     * Fetch all fixtures (match schedule)
     * Includes fixture difficulty ratings (FDR)
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getFixtures() {
        String cacheKey = "fixtures";
        
        CacheEntry entry = cache.get(cacheKey);
        if (entry != null && !entry.isExpired()) {
            return (List<Map<String, Object>>) entry.data;
        }
        
        String url = fplBaseUrl + "/fixtures/";
        List<Map<String, Object>> response = restTemplate.getForObject(url, List.class);
        
        if (response != null) {
            cache.put(cacheKey, new CacheEntry(response));
        }
        
        return response;
    }
    
    /**
     * Get a user's team information by their FPL Team ID
     * No authentication required - FPL API is public!
     */
    public Map<String, Object> getUserTeam(String fplId) {
        String url = fplBaseUrl + "/entry/" + fplId + "/";
        return restTemplate.getForObject(url, Map.class);
    }
    
    /**
     * Get a user's picks (selected players) for a specific gameweek
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getUserPicks(String fplId, int gameweek) {
        String url = fplBaseUrl + "/entry/" + fplId + "/event/" + gameweek + "/picks/";
        return restTemplate.getForObject(url, Map.class);
    }
    
    /**
     * Get the current gameweek number
     * Finds the event where is_current = true
     */
    @SuppressWarnings("unchecked")
    public int getCurrentGameweek() {
        Map<String, Object> bootstrap = getBootstrapData();
        List<Map<String, Object>> events = (List<Map<String, Object>>) bootstrap.get("events");
        
        return events.stream()
                .filter(event -> Boolean.TRUE.equals(event.get("is_current")))
                .findFirst()
                .map(event -> (Integer) event.get("id"))
                .orElse(1);  // Default to GW1 if no current gameweek
    }
}
```

### Key Concepts Explained:

#### `@Service` Annotation:
Marks this class as a Spring service bean. Spring will create one instance and inject it wherever needed.

#### `RestTemplate`:
Spring's built-in HTTP client for making REST API calls.

```java
// GET request - returns response body as specified type
Map<String, Object> data = restTemplate.getForObject(url, Map.class);

// POST request - sends body and returns response
ResponseEntity<String> response = restTemplate.postForEntity(url, requestBody, String.class);
```

#### Simple Caching Pattern:
We use a `ConcurrentHashMap` with timestamp-based expiration:

```java
// Check if cached and not expired
if (cache.containsKey(key) && !cache.get(key).isExpired()) {
    return cache.get(key).data;
}

// Otherwise fetch fresh data and cache it
Object freshData = fetchFromApi();
cache.put(key, new CacheEntry(freshData));
return freshData;
```

---

## 4.3 Create the Player Service

This service enriches the raw FPL data with additional useful fields like team names and position labels.

**File:** `server/src/main/java/com/fpl/server/service/PlayerService.java`

```java
package com.fpl.server.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Player Service
 * 
 * Business logic for processing player data.
 * Takes raw FPL API data and enriches it with:
 * - Team names (instead of just team IDs)
 * - Position labels (GK, DEF, MID, FWD instead of 1, 2, 3, 4)
 * - Formatted price (8.5 instead of 85)
 * - Full name (first_name + second_name)
 * - Placeholder for predicted points (ML service will fill this later)
 */
@Service
public class PlayerService {
    
    // @Autowired: Spring automatically injects the FplApiService instance
    @Autowired
    private FplApiService fplApiService;
    
    /**
     * Get all players with enriched data
     * 
     * The raw FPL API uses IDs for teams and positions.
     * This method converts those to human-readable names.
     */
    public List<Map<String, Object>> getAllPlayersEnriched() {
        // Fetch raw data
        List<Map<String, Object>> players = fplApiService.getAllPlayers();
        List<Map<String, Object>> teams = fplApiService.getAllTeams();
        List<Map<String, Object>> elementTypes = fplApiService.getElementTypes();
        
        // Create lookup maps: ID -> Name
        // Example: { 1: "ARS", 2: "AVL", ... }
        Map<Integer, String> teamMap = teams.stream()
                .collect(Collectors.toMap(
                        t -> (Integer) t.get("id"),
                        t -> (String) t.get("short_name")
                ));
        
        // Example: { 1: "GKP", 2: "DEF", 3: "MID", 4: "FWD" }
        Map<Integer, String> positionMap = elementTypes.stream()
                .collect(Collectors.toMap(
                        e -> (Integer) e.get("id"),
                        e -> (String) e.get("singular_name_short")
                ));
        
        // Enrich each player with additional fields
        return players.stream()
                .map(player -> {
                    // Create a new map with all original fields plus new ones
                    Map<String, Object> enriched = new HashMap<>(player);
                    
                    Integer teamId = (Integer) player.get("team");
                    Integer positionId = (Integer) player.get("element_type");
                    
                    // Add team name (e.g., "ARS", "MCI", "LIV")
                    enriched.put("team_name", teamMap.getOrDefault(teamId, "Unknown"));
                    
                    // Add position label (e.g., "GKP", "DEF", "MID", "FWD")
                    enriched.put("position", positionMap.getOrDefault(positionId, "Unknown"));
                    
                    // Convert price from integer (85) to decimal (8.5)
                    Object nowCostObj = player.get("now_cost");
                    if (nowCostObj instanceof Integer) {
                        enriched.put("price", ((Integer) nowCostObj) / 10.0);
                    }
                    
                    // Combine first and last name
                    String firstName = (String) player.get("first_name");
                    String secondName = (String) player.get("second_name");
                    enriched.put("full_name", firstName + " " + secondName);
                    
                    // Placeholder for ML predictions (will be filled by ML service later)
                    enriched.put("predicted_points", 0.0);
                    
                    return enriched;
                })
                .collect(Collectors.toList());
    }
    
    /**
     * Merge ML predictions with player data
     * 
     * @param players List of player objects
     * @param predictions Map of player ID -> predicted points
     * @return Players with predicted_points field updated
     */
    public List<Map<String, Object>> enrichPlayersWithPredictions(
            List<Map<String, Object>> players,
            Map<String, Double> predictions) {
        
        return players.stream()
                .map(player -> {
                    Map<String, Object> enriched = new HashMap<>(player);
                    Object playerId = player.get("id");
                    String playerIdStr = String.valueOf(playerId);
                    enriched.put("predicted_points", predictions.getOrDefault(playerIdStr, 0.0));
                    return enriched;
                })
                .collect(Collectors.toList());
    }
}
```

### Java Streams Explained:

Java Streams provide a functional way to process collections:

```java
// Filter: Keep only items matching condition
list.stream().filter(x -> x > 10).collect(Collectors.toList());

// Map: Transform each item
list.stream().map(x -> x * 2).collect(Collectors.toList());

// Collect to Map: Create key-value pairs
list.stream().collect(Collectors.toMap(
    item -> item.getId(),     // Key function
    item -> item.getName()    // Value function
));
```

---

## 4.4 Create the Player Controller

The REST controller exposes our player data through HTTP endpoints.

**File:** `server/src/main/java/com/fpl/server/controller/PlayerController.java`

```java
package com.fpl.server.controller;

import com.fpl.server.service.FplApiService;
import com.fpl.server.service.PlayerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Player Controller
 * 
 * REST API endpoints for player data.
 * 
 * Endpoints:
 * - GET /api/players           → All players with enriched data
 * - GET /api/players/{id}      → Single player by ID
 * - GET /api/players/teams     → All Premier League teams
 * - GET /api/players/fixtures  → All fixtures
 * - GET /api/players/gameweek/current → Current gameweek number
 */
@RestController
@RequestMapping("/api/players")
public class PlayerController {
    
    @Autowired
    private FplApiService fplApiService;
    
    @Autowired
    private PlayerService playerService;
    
    /**
     * GET /api/players
     * Returns all 650+ players with enriched data
     */
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getAllPlayers() {
        try {
            List<Map<String, Object>> players = playerService.getAllPlayersEnriched();
            return ResponseEntity.ok(players);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * GET /api/players/{id}
     * Returns a single player by their FPL ID
     * 
     * @PathVariable extracts the {id} from the URL path
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getPlayer(@PathVariable Integer id) {
        try {
            List<Map<String, Object>> players = playerService.getAllPlayersEnriched();
            
            // Find player with matching ID using Stream
            return players.stream()
                    .filter(p -> id.equals(p.get("id")))
                    .findFirst()
                    .map(ResponseEntity::ok)  // If found, return 200 OK
                    .orElse(ResponseEntity.notFound().build());  // If not found, return 404
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * GET /api/players/teams
     * Returns all 20 Premier League teams
     */
    @GetMapping("/teams")
    public ResponseEntity<List<Map<String, Object>>> getAllTeams() {
        try {
            List<Map<String, Object>> teams = fplApiService.getAllTeams();
            return ResponseEntity.ok(teams);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * GET /api/players/fixtures
     * Returns all fixtures for the season
     */
    @GetMapping("/fixtures")
    public ResponseEntity<List<Map<String, Object>>> getFixtures() {
        try {
            List<Map<String, Object>> fixtures = fplApiService.getFixtures();
            return ResponseEntity.ok(fixtures);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * GET /api/players/gameweek/current
     * Returns the current gameweek number
     */
    @GetMapping("/gameweek/current")
    public ResponseEntity<Map<String, Object>> getCurrentGameweek() {
        try {
            int gw = fplApiService.getCurrentGameweek();
            return ResponseEntity.ok(Map.of("current_gameweek", gw));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}
```

### Annotation Cheat Sheet:

| Annotation | Purpose |
|------------|---------|
| `@GetMapping` | Handle HTTP GET requests |
| `@PostMapping` | Handle HTTP POST requests |
| `@PathVariable` | Extract value from URL path (`/players/{id}`) |
| `@RequestParam` | Extract query parameter (`/players?team=arsenal`) |
| `@RequestBody` | Parse JSON request body into object |

---

## 4.5 Test the New Endpoints

**Restart the Spring Boot server** (stop with `Ctrl+C`, then restart):

```bash
cd /home/atibhav/repos/fpl/server
./mvnw spring-boot:run
```

**Test the endpoints in your browser:**

1. **All players:** http://localhost:8080/api/players
   - Returns 650+ player objects (takes a few seconds first time)

2. **Single player:** http://localhost:8080/api/players/1
   - Returns one player object

3. **All teams:** http://localhost:8080/api/players/teams
   - Returns 20 team objects

4. **Fixtures:** http://localhost:8080/api/players/fixtures
   - Returns all match fixtures

5. **Current gameweek:** http://localhost:8080/api/players/gameweek/current
   - Returns `{"current_gameweek": X}`

---

## 4.6 Project Structure After Step 4

```
server/src/main/java/com/fpl/server/
├── ServerApplication.java
├── config/
│   └── CorsConfig.java
├── controller/
│   ├── HealthController.java
│   └── PlayerController.java       # NEW
└── service/
    ├── FplApiService.java          # NEW
    └── PlayerService.java          # NEW
```

---

# Step 5: Display Players in React

**Goal:** Create a React page that fetches and displays players from our Spring Boot backend with filtering and sorting.

## 5.1 Install React Router

We need routing to navigate between pages (Home, Players, Squad Builder, etc.).

```bash
cd /home/atibhav/repos/fpl/client
npm install react-router-dom
```

## 5.2 Create the PlayerCard Component

A reusable component to display individual player information.

**File:** `client/src/components/PlayerCard.js`

```javascript
import React from 'react';
import './PlayerCard.css';

/**
 * PlayerCard Component
 * 
 * Displays a single player's information in a card format.
 * 
 * Props:
 * - player: Object containing player data from the API
 * - onSelect: Function called when card is clicked (optional)
 * - isSelected: Boolean indicating if this player is selected (optional)
 * 
 * Key Concepts:
 * - Props: Data passed from parent to child component
 * - Conditional styling: Using ternary operators for dynamic classes
 * - Object destructuring in function parameters
 */
function PlayerCard({ player, onSelect, isSelected }) {
  // Helper function to determine color based on predicted points
  const getColorByPoints = (points) => {
    if (points >= 6) return '#00ff87';  // Green for high
    if (points >= 4) return '#ffc107';  // Yellow for medium
    return '#ff5252';                    // Red for low
  };

  // Position-specific colors matching FPL's color scheme
  const positionColors = {
    'GKP': '#ebff00',  // Yellow for goalkeepers
    'DEF': '#00ff87',  // Green for defenders
    'MID': '#05f0ff',  // Cyan for midfielders
    'FWD': '#e90052'   // Pink for forwards
  };

  return (
    <div 
      className={`player-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect && onSelect(player)}
    >
      {/* Position badge with color coding */}
      <div 
        className="position-badge"
        style={{ backgroundColor: positionColors[player.position] || '#888' }}
      >
        {player.position}
      </div>
      
      {/* Player name and team */}
      <div className="player-info">
        <div className="player-name">{player.web_name || player.second_name}</div>
        <div className="player-team">{player.team_name}</div>
      </div>
      
      {/* Stats: Price, Points, Form */}
      <div className="player-stats">
        <div className="stat">
          <span className="stat-label">Price</span>
          <span className="stat-value">£{player.price}m</span>
        </div>
        <div className="stat">
          <span className="stat-label">Points</span>
          <span className="stat-value">{player.total_points}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Form</span>
          <span className="stat-value">{player.form}</span>
        </div>
      </div>
      
      {/* Predicted points (will be filled by ML service later) */}
      <div 
        className="predicted-points"
        style={{ color: getColorByPoints(player.predicted_points) }}
      >
        {player.predicted_points.toFixed(1)} xPts
      </div>
    </div>
  );
}

export default PlayerCard;
```

**File:** `client/src/components/PlayerCard.css`

```css
.player-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: #16213e;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.player-card:hover {
  background-color: #1a2744;
  transform: translateY(-2px);
}

.player-card.selected {
  border-color: #00ff87;
  background-color: #1a3a2e;
}

.position-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1a1a2e;
  min-width: 36px;
  text-align: center;
}

.player-info {
  flex: 1;
  min-width: 0;  /* Allows text truncation to work */
}

.player-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;  /* Shows "..." for long names */
}

.player-team {
  font-size: 0.8rem;
  color: #888;
}

.player-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 50px;
}

.stat-label {
  font-size: 0.7rem;
  color: #666;
  text-transform: uppercase;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
}

.predicted-points {
  font-size: 1rem;
  font-weight: 700;
  min-width: 60px;
  text-align: right;
}
```

---

## 5.3 Create the PlayersPage

A full page component that fetches players and provides filtering/sorting.

**File:** `client/src/pages/PlayersPage.js`

```javascript
import React, { useState, useEffect } from 'react';
import { getPlayers } from '../services/api';
import PlayerCard from '../components/PlayerCard';
import './PlayersPage.css';

/**
 * PlayersPage Component
 * 
 * Displays all players with filtering and sorting options.
 * 
 * Features:
 * - Fetches 700+ players from backend on load
 * - Search by player name
 * - Filter by position (GK, DEF, MID, FWD)
 * - Filter by team
 * - Sort by points, price, form, or predicted points
 * 
 * Key Concepts:
 * - Multiple useState hooks for different pieces of state
 * - useEffect for data fetching on component mount
 * - Controlled inputs (value + onChange)
 * - Array methods: filter, sort, map
 */
function PlayersPage() {
  // State for player data
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for filters (all controlled inputs)
  const [filters, setFilters] = useState({
    position: 'ALL',
    team: 'ALL',
    search: '',
    sortBy: 'total_points'
  });

  // Fetch players when component mounts
  useEffect(() => {
    loadPlayers();
  }, []);

  const loadPlayers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPlayers();
      setPlayers(data);
    } catch (err) {
      setError('Failed to load players. Is the backend running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Extract unique team names for the dropdown
  const getUniqueTeams = () => {
    const teams = [...new Set(players.map(p => p.team_name))];
    return teams.sort();
  };

  // Apply filters and sorting
  const filteredPlayers = players
    .filter(p => {
      // Position filter
      if (filters.position !== 'ALL' && p.position !== filters.position) return false;
      // Team filter
      if (filters.team !== 'ALL' && p.team_name !== filters.team) return false;
      // Search filter (checks both full name and web name)
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const fullName = (p.full_name || '').toLowerCase();
        const webName = (p.web_name || '').toLowerCase();
        if (!fullName.includes(searchLower) && !webName.includes(searchLower)) {
          return false;
        }
      }
      return true;
    })
    .sort((a, b) => {
      // Sort descending (highest first)
      switch (filters.sortBy) {
        case 'price':
          return b.price - a.price;
        case 'form':
          return parseFloat(b.form) - parseFloat(a.form);
        case 'predicted_points':
          return b.predicted_points - a.predicted_points;
        case 'total_points':
        default:
          return b.total_points - a.total_points;
      }
    });

  // Loading state
  if (loading) {
    return (
      <div className="players-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading players...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="players-page">
        <div className="error-container">
          <p>❌ {error}</p>
          <button onClick={loadPlayers}>Retry</button>
        </div>
      </div>
    );
  }

  // Main render
  return (
    <div className="players-page">
      <header className="page-header">
        <h1>Players</h1>
        <p className="player-count">{filteredPlayers.length} players</p>
      </header>

      {/* Filter controls */}
      <div className="filters-bar">
        <input
          type="text"
          placeholder="Search players..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="search-input"
        />

        <select
          value={filters.position}
          onChange={(e) => setFilters({ ...filters, position: e.target.value })}
          className="filter-select"
        >
          <option value="ALL">All Positions</option>
          <option value="GKP">Goalkeepers</option>
          <option value="DEF">Defenders</option>
          <option value="MID">Midfielders</option>
          <option value="FWD">Forwards</option>
        </select>

        <select
          value={filters.team}
          onChange={(e) => setFilters({ ...filters, team: e.target.value })}
          className="filter-select"
        >
          <option value="ALL">All Teams</option>
          {getUniqueTeams().map(team => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>

        <select
          value={filters.sortBy}
          onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
          className="filter-select"
        >
          <option value="total_points">Sort by Points</option>
          <option value="price">Sort by Price</option>
          <option value="form">Sort by Form</option>
          <option value="predicted_points">Sort by xPts</option>
        </select>
      </div>

      {/* Player list (limited to 100 for performance) */}
      <div className="players-list">
        {filteredPlayers.slice(0, 100).map(player => (
          <PlayerCard 
            key={player.id} 
            player={player}
          />
        ))}
        {filteredPlayers.length > 100 && (
          <p className="more-players">
            Showing first 100 of {filteredPlayers.length} players
          </p>
        )}
      </div>
    </div>
  );
}

export default PlayersPage;
```

---

## 5.4 Update App.js with Routing

Add navigation and routing to switch between pages.

**File:** `client/src/App.js`

```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PlayersPage from './pages/PlayersPage';
import './App.css';

/**
 * HomePage Component
 * 
 * Landing page with navigation cards to different features.
 */
function HomePage() {
  return (
    <div className="home-page">
      <h1>FPL ML Team Builder</h1>
      <p className="tagline">Build your optimal Fantasy Premier League team using machine learning predictions</p>
      
      <div className="feature-cards">
        {/* Link component for client-side navigation (no page reload) */}
        <Link to="/players" className="feature-card">
          <h2>📊 Browse Players</h2>
          <p>View all 700+ Premier League players with stats, prices, and predicted points</p>
        </Link>
        
        {/* Disabled cards for features not yet implemented */}
        <div className="feature-card disabled">
          <h2>⚽ Squad Builder</h2>
          <p>Build and optimize your dream team (coming soon)</p>
        </div>
        
        <div className="feature-card disabled">
          <h2>🤖 ML Predictions</h2>
          <p>AI-powered points predictions (coming soon)</p>
        </div>
      </div>
    </div>
  );
}

/**
 * App Component (Root)
 * 
 * Sets up routing and navigation for the entire application.
 * 
 * React Router Concepts:
 * - BrowserRouter: Enables client-side routing using browser history
 * - Routes: Container for all route definitions
 * - Route: Maps a URL path to a component
 * - Link: Navigation without page reload (like <a> but for React)
 */
function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation bar */}
        <nav className="navbar">
          <Link to="/" className="nav-brand">FPL ML Builder</Link>
          <div className="nav-links">
            <Link to="/">Home</Link>
            <Link to="/players">Players</Link>
          </div>
        </nav>
        
        {/* Page content based on current route */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/players" element={<PlayersPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
```

---

## 5.5 Test the Players Page

1. **Make sure Spring Boot is running** on port 8080
2. **React should auto-reload** if `npm start` is still running
3. **Visit** `http://localhost:3000`
4. **Click** "Browse Players" or the "Players" nav link

You should see:
- A list of players with position badges, names, teams, and stats
- Search box to filter by name
- Dropdowns to filter by position and team
- Sort options for points, price, form

---

## 5.6 React Concepts Recap

### Controlled Components

Form inputs whose values are controlled by React state:

```javascript
// State holds the value
const [search, setSearch] = useState('');

// Input displays state and updates it on change
<input 
  value={search} 
  onChange={(e) => setSearch(e.target.value)} 
/>
```

### Lifting State Up

When multiple components need the same state, lift it to their common parent.

### Conditional Rendering

Show different content based on state:

```javascript
{loading && <Spinner />}
{error && <ErrorMessage />}
{data && <DataList data={data} />}
```

### Array Methods for Data Transformation

```javascript
// Filter: Keep items matching condition
players.filter(p => p.position === 'FWD')

// Sort: Order items
players.sort((a, b) => b.points - a.points)

// Map: Transform each item
players.map(p => <PlayerCard key={p.id} player={p} />)

// Slice: Limit results
players.slice(0, 100)
```

---

## 5.7 Project Structure After Step 5

```
client/src/
├── App.js                    # Root component with routing
├── App.css                   # Global and navbar styles
├── index.js                  # Entry point
├── services/
│   └── api.js                # API calls to backend
├── components/
│   ├── PlayerCard.js         # NEW: Player card component
│   └── PlayerCard.css        # NEW: Player card styles
├── pages/
│   ├── PlayersPage.js        # NEW: Players list page
│   └── PlayersPage.css       # NEW: Players page styles
└── styles/                   # (empty, for future use)
```

---

# Step 6: FastAPI ML Service Setup

## 6.1 Why FastAPI? (Framework Trade-off Analysis)

Before building the ML microservice, we evaluated three Python frameworks. Here's our analysis:

### The Three Options

| Framework | Description | Use Case |
|-----------|-------------|----------|
| **Flask** | Lightweight, minimal micro-framework | Simple APIs, beginners |
| **Django** | Full-featured "batteries included" framework | Large web apps with ORM, auth |
| **FastAPI** | Modern async framework with type hints | APIs, ML services |

### Detailed Comparison

| Aspect | Flask | FastAPI | Django |
|--------|-------|---------|--------|
| **Setup Complexity** | Minimal (~5 files) | Minimal (~5 files) | Heavy (~15+ files) |
| **Auto API Docs** | Manual (add Swagger) | ✅ Built-in Swagger/ReDoc | Manual |
| **Type Validation** | Manual | ✅ Pydantic (automatic) | Manual |
| **Async Support** | Add-on | ✅ Native | Limited |
| **Performance** | Good | ⚡ Fastest Python framework | Good |
| **Learning Curve** | Easiest | Easy-Medium | Steepest |
| **ML/AI Popularity** | Common | 🔥 Very popular (growing) | Less common |
| **Resume Value (2024)** | Good | 🔥 Excellent | Good |

### Why We Chose FastAPI

1. **Automatic API Documentation**
   - Visit `/docs` → Interactive Swagger UI for free
   - Great for demos and portfolio showcases
   - No manual documentation needed

2. **Type Validation with Pydantic**
   - Define request/response models once
   - Automatic validation (wrong types = 422 error with clear message)
   - IDE autocomplete works perfectly

3. **Modern Python**
   - Shows you know async/await, type hints
   - Industry-standard for ML APIs (OpenAI, Uber, Netflix use it)

4. **Performance**
   - Important when processing 600+ players
   - Async support for concurrent requests

5. **Resume Value**
   - FastAPI is the "hot" framework in 2024
   - Shows modern Python skills

### Why NOT Flask?

Flask would work fine, but:
- No built-in API docs (need swagger-ui manually)
- No automatic request validation
- Synchronous by default
- Less impressive on resume in 2024

### Why NOT Django?

Django is overkill because:
- We already have Spring Boot handling database (PostgreSQL + JPA)
- We don't need Django's ORM, admin panel, or authentication
- More boilerplate code for a simple ML API
- Slower cold starts on free hosting

---

## 6.2 FastAPI Project Structure

```
ml-service/
├── main.py                      # FastAPI entry point
├── requirements.txt             # Python dependencies
├── venv/                        # Virtual environment (NOT committed to Git)
├── ml/                          # ML models and prediction logic
│   ├── __init__.py
│   └── predictor.py             # Prediction functions
├── optimization/                # PuLP squad optimization
│   ├── __init__.py
│   └── team_optimizer.py        # Optimization functions
├── data/                        # Data processing
│   ├── __init__.py
│   └── raw/                     # Vaastav dataset (will be downloaded)
└── models/                      # Saved ML model files (.pkl, .h5)
```

---

## 6.3 Setting Up the FastAPI Service

### Step 1: Create Directory Structure

```bash
cd /home/atibhav/repos/fpl/ml-service
mkdir -p ml optimization data data/raw models
```

### Step 2: Create `requirements.txt`

```text
# FastAPI and server
fastapi==0.109.0
uvicorn[standard]==0.27.0

# ML libraries
pandas==2.1.4
numpy==1.26.3
scikit-learn==1.4.0
joblib==1.3.2

# Optimization
pulp==2.7.0

# HTTP requests (for fetching external data)
requests==2.31.0

# For production deployment
gunicorn==21.2.0
```

**What Each Package Does:**

| Package | Purpose |
|---------|---------|
| `fastapi` | The web framework |
| `uvicorn` | ASGI server to run FastAPI |
| `pandas` | Data manipulation (DataFrames) |
| `numpy` | Numerical operations |
| `scikit-learn` | ML algorithms (LinearRegression, RandomForest, SVR) |
| `joblib` | Save/load trained models |
| `pulp` | Linear Programming for optimization |
| `requests` | HTTP client for external APIs |
| `gunicorn` | Production-grade WSGI server |

### Step 3: Create Python Virtual Environment

```bash
cd /home/atibhav/repos/fpl/ml-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Why Virtual Environment?**
- Isolates project dependencies from system Python
- Prevents version conflicts between projects
- The `venv/` folder contains ~10,000+ files — that's why we add it to `.gitignore`

---

## 6.4 Main FastAPI Application (`main.py`)

```python
"""
FPL ML Service - FastAPI Application

This is the main entry point for the ML microservice.
It handles:
1. Player points predictions using trained ML models
2. Squad optimization using PuLP linear programming

The Spring Boot backend calls this service internally.
Users never interact with this directly.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

# =============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# =============================================================================
# Pydantic models define the shape of data coming in and going out.
# FastAPI uses these for:
# 1. Automatic validation (wrong types = 422 error)
# 2. Auto-generated API documentation
# 3. IDE autocomplete support

class PlayerFeatures(BaseModel):
    """Features for a single player prediction"""
    id: int
    name: str
    position: str  # GK, DEF, MID, FWD
    team: str
    price: float
    form: Optional[float] = 0.0
    total_points: Optional[int] = 0
    minutes: Optional[int] = 0
    goals_scored: Optional[int] = 0
    assists: Optional[int] = 0
    clean_sheets: Optional[int] = 0


class PredictionRequest(BaseModel):
    """Request body for /predict endpoint"""
    players: List[PlayerFeatures]


class PredictionResponse(BaseModel):
    """Response from /predict endpoint"""
    predictions: Dict[str, float]  # {player_id: predicted_points}


class OptimizeRequest(BaseModel):
    """Request body for /optimize/squad endpoint"""
    players: List[Dict]  # Players with predicted_points
    budget: float = 100.0


class OptimizeResponse(BaseModel):
    """Response from /optimize/squad endpoint"""
    squad: List[Dict]
    total_cost: float
    expected_points: float
    status: str


class HealthResponse(BaseModel):
    """Response from /health endpoint"""
    status: str
    message: str
    version: str


# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="FPL ML Service",
    description="Machine Learning predictions and squad optimization for Fantasy Premier League",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI at /docs
    redoc_url="/redoc"     # ReDoc at /redoc
)

# CORS Configuration
# Allows Spring Boot backend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your backend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint.
    
    Used by:
    - Spring Boot to verify ML service is running
    - Render.com for health monitoring
    - Manual testing
    """
    return HealthResponse(
        status="ok",
        message="FPL ML Service is running!",
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
def predict_points(request: PredictionRequest):
    """
    Predict points for a list of players.
    
    This endpoint:
    1. Receives player data from Spring Boot
    2. Extracts features for each player
    3. Runs predictions through trained ML models
    4. Returns predicted points per player
    
    For now, returns dummy predictions (form * 1.5).
    Will be replaced with actual ML model predictions.
    """
    predictions = {}
    
    for player in request.players:
        # PLACEHOLDER: Simple prediction based on form
        # TODO: Replace with actual ML model prediction
        predicted = float(player.form) * 1.5 if player.form else 2.0
        predictions[str(player.id)] = round(predicted, 1)
    
    return PredictionResponse(predictions=predictions)


@app.post("/optimize/squad", response_model=OptimizeResponse)
def optimize_squad(request: OptimizeRequest):
    """
    Optimize squad selection using Linear Programming.
    
    This endpoint:
    1. Receives all players with predicted points
    2. Uses PuLP to solve the optimization problem
    3. Returns the optimal 15-player squad
    
    Constraints:
    - Exactly 15 players
    - Budget limit (default £100m)
    - 2 GK, 5 DEF, 5 MID, 3 FWD
    - Max 3 players per team
    
    For now, returns a simple sorted selection.
    TODO: Implement full PuLP optimization.
    """
    # Placeholder implementation - will be replaced with PuLP
    players = request.players
    budget = request.budget
    
    # ... (simplified greedy selection)
    
    return OptimizeResponse(
        squad=selected,
        total_cost=round(total_cost, 1),
        expected_points=round(expected_points, 1),
        status="Optimal" if len(selected) == 15 else "Partial"
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run with: python main.py
    # Or: uvicorn main:app --reload --port 5001
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True  # Auto-reload on code changes (dev only)
    )
```

---

## 6.5 Key FastAPI Concepts

### Pydantic Models

Pydantic is FastAPI's secret weapon. Define your data once:

```python
class PlayerFeatures(BaseModel):
    id: int                           # Required, must be integer
    name: str                         # Required, must be string
    position: str                     # Required, must be string
    form: Optional[float] = 0.0       # Optional, defaults to 0.0
```

**What Pydantic Gives You:**
1. **Validation**: Wrong types automatically return 422 error
2. **Documentation**: Shows up in Swagger UI
3. **Type Hints**: IDE autocomplete works perfectly
4. **Serialization**: Converts to/from JSON automatically

### Decorators for Endpoints

```python
@app.get("/health")           # HTTP GET request to /health
@app.post("/predict")         # HTTP POST request to /predict
@app.put("/update")           # HTTP PUT request to /update
@app.delete("/remove")        # HTTP DELETE request to /remove
```

### Response Models

```python
@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(...)  # Must match the model
```

- `response_model` tells FastAPI what shape the response should be
- Automatic validation of your response
- Generates correct API documentation

### Path Parameters vs Query Parameters

```python
# Path parameter: /players/123
@app.get("/players/{player_id}")
def get_player(player_id: int):
    ...

# Query parameter: /players?position=FWD
@app.get("/players")
def get_players(position: Optional[str] = None):
    ...
```

---

## 6.6 Running the FastAPI Service

### Start the Server

```bash
cd /home/atibhav/repos/fpl/ml-service
source venv/bin/activate
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --port 5001
```

### Test the Endpoints

**Health Check:**
```bash
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "FPL ML Service is running!",
  "version": "1.0.0"
}
```

**Swagger UI (Interactive Docs):**
Open in browser: `http://localhost:5001/docs`

This gives you:
- Interactive API documentation
- Try endpoints directly from browser
- See request/response schemas
- Great for demos!

---

## 6.7 Important: `.gitignore` for Python

The `venv/` folder contains ~10,000+ package files. **NEVER commit it to Git.**

Our `.gitignore` includes:

```gitignore
# Python virtual environment
venv/
.venv/
env/

# Python cache
__pycache__/
*.pyc

# ML model files (can be large)
*.pkl
*.h5
```

**Why?**
- `venv/` can be regenerated with `pip install -r requirements.txt`
- It's platform-specific (Linux vs Mac vs Windows)
- It's huge (~400MB+)

---

## 6.8 Project Structure After Step 6

```
fpl/
├── .gitignore                    # Ignores venv, node_modules, etc.
├── DEVELOPMENT.md                # This guide
├── plan.md                       # Project plan
├── client/                       # React frontend
│   └── ...
├── server/                       # Spring Boot backend
│   └── ...
└── ml-service/                   # NEW: FastAPI ML service
    ├── main.py                   # FastAPI app with endpoints
    ├── requirements.txt          # Python dependencies
    ├── venv/                     # Virtual environment (NOT in Git)
    ├── ml/
    │   ├── __init__.py
    │   └── predictor.py          # Prediction placeholder
    ├── optimization/
    │   ├── __init__.py
    │   └── team_optimizer.py     # Optimization placeholder
    ├── data/
    │   ├── __init__.py
    │   └── raw/                  # For Vaastav dataset
    └── models/                   # For saved .pkl models
```

---

## 6.9 Next Steps

Now that FastAPI is set up with placeholder endpoints, we need to:

1. **Download Vaastav FPL dataset** → Real historical data
2. **Create data preprocessing pipeline** → Clean and engineer features
3. **Train Linear Regression baseline** → First real ML model
4. **Connect Spring Boot to FastAPI** → End-to-end predictions

