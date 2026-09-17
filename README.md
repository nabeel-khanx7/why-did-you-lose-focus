# Why Did You Lose Focus? AI

An AI-powered focus analysis system that tracks computer activity, detects focus loss, and identifies the possible reasons behind distractions.

## 🎯 Project Goal

The goal of this project is to understand **why a user loses focus** during study or work sessions.

Instead of simply measuring screen time, the system analyzes activity patterns such as:

- Application usage
- Application switching
- Idle time
- Session duration
- Distraction patterns

and eventually uses Machine Learning to identify probable focus-loss reasons.

## 🚀 Current Status

### Phase 1 — Project Setup
- [x] Python environment
- [x] Project structure
- [x] Required libraries
- [x] Git repository
- [x] `.gitignore`
- [x] Basic activity tracker

### Phase 2 — Activity Tracking
- [x] Detect active macOS application
- [ ] Track application duration
- [ ] Detect application switching
- [ ] Detect idle time
- [ ] Store activity data

### Phase 3 — Focus Detection
- [ ] Focus score
- [ ] Productive vs distracting activity
- [ ] Focus-loss events

### Phase 4 — Machine Learning
- [ ] Dataset creation
- [ ] Feature engineering
- [ ] ML model
- [ ] Model evaluation

### Phase 5 — AI Analysis
- [ ] Identify probable focus-loss reason
- [ ] Personalized recommendations
- [ ] Focus pattern analysis

### Phase 6 — Dashboard
- [ ] Real-time dashboard
- [ ] Daily analytics
- [ ] Weekly analytics
- [ ] Focus history

## 🛠️ Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Psutil
- FastAPI
- React
- OpenCV
- MediaPipe
- SQLite

## 📁 Project Structure

```text
why-did-you-lose-focus/
│
├── src/
│   └── activity_tracker.py
│
├── data/
├── models/
├── dashboard/
├── venv/
├── .gitignore
└── README.md