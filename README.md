# ReliefIQ

AI-powered decision support system for flood disaster relief planning in Kerala, India.

**Live demo:** https://reliefiq-m8llzmrmheqtcakjxfapni.streamlit.app
**API docs:** https://reliefiq.onrender.com/docs

## What it does
Predicts flood severity per district using real 2018 Kerala flood data,
converts predictions into operational decisions via a transparent Decision
Engine, forecasts resource demand, and computes a priority-weighted,
equity-capped resource allocation plan using linear programming.

## Architecture
- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy + Alembic), hosted on Supabase
- **Prediction:** Transparent composite risk score — ML approaches
  (XGBoost, Logistic Regression) were rigorously tested via LOOCV and did
  not outperform a majority-class baseline at n=13 samples (see ADR-008)
- **Optimization:** Linear programming (PuLP), priority-weighted with an
  equity cap preventing any single district from dominating allocation
- **Deployment:** Docker, Render (API), Supabase (database), Streamlit
  Community Cloud (dashboard)

## Data
Real Kerala 2018 flood event data, real Census India population figures,
real historical rainfall (1901-2015). Infrastructure data is disclosed
synthetic, scaled from real population (see data/DATA_SOURCES.md).

## Key engineering decisions
Full trail in docs/adr/ — including why ML was rejected in favor of a
transparent scoring approach, why linear programming was used for
allocation, and why an equity cap was added after observing winner-take-all
allocation behavior during testing.

## Local setup
\`\`\`bash
git clone https://github.com/0810aparna/ReliefIQ.git
cd ReliefIQ
docker-compose up -d
python data/load_to_db.py
streamlit run app/main.py
\`\`\`

## Limitations
- Model calibrated on a single flood season (2018) — see models/saved/model_card.md
- Rainfall data is subdivision-level, not fully district-granular
- Infrastructure figures are synthetic, scaled from real population