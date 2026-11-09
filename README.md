# CHURN.AI — Customer Churn Prediction

CHURN.AI is a single-service churn prediction application. A React dashboard collects customer data, and a FastAPI backend validates it and sends it to the supplied Scikit-learn pipeline. The same service serves the production frontend and API.

## Problem

Customer teams need a consistent way to examine churn risk from account and service information. This application turns the existing Logistic Regression pipeline into an interactive single-customer and CSV prediction workflow. A prediction is an estimate; the application does not receive or confirm real churn outcomes.

## Features

- Single-customer form with constrained service selections and model-backed prediction.
- CSV upload with schema, numeric, category, missing-value and service-combination validation.
- Bulk results with original columns, probability, binary prediction and risk label; downloadable CSV.
- Dashboard and customer exploration based only on predictions held in the current browser.
- Model status, feature schema and historical test-set evaluation information.
- Responsive React interface served by FastAPI in production.

## Technology

React, Vite, Tailwind CSS, Recharts, Lucide React, FastAPI, Pydantic, Pandas, NumPy, Scikit-learn and Joblib. Docker builds the frontend and runs the combined service; Render can deploy it as one web service.

## Screenshots

Add current application screenshots here:

- `docs/screenshots/dashboard.png`
- `docs/screenshots/prediction.png`
- `docs/screenshots/bulk-results.png`

## Machine learning methodology

The application loads the existing `Churn_predict.pkl` pipeline once during FastAPI startup and uses its `predict_proba` output. The probability is taken from the column whose `classes_` entry is `Yes`, rather than assuming class order. The trained model is not retrained or replaced.

The public input schema contains these 19 features: `SeniorCitizen`, `tenure`, `MonthlyCharges`, `TotalCharges`, `gender`, `Partner`, `Dependents`, `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`, `PaymentMethod`. The supplied artifact's recorded feature order is respected during inference by feature name.

The form and API reject invalid categories, incomplete rows, invalid numeric values and inconsistent service selections. The bulk endpoint rejects a whole file when any row fails validation; it does not silently drop rows.

**The current model provides a baseline for customer churn prediction. Its performance may be improved in future updates through further experimentation, feature engineering, hyperparameter tuning and evaluation of alternative algorithms.**

**Future updates may improve accuracy and other evaluation metrics; however, improvements are not guaranteed.**

## Model evaluation

The following values are the provided historical held-out test-set results. They are not live prediction accuracy.

| Metric | Value |
|---|---:|
| Accuracy | 78.39% |
| Churn precision | 58% |
| Churn recall | 68% |
| Churn F1-score | 63% |

## Risk classification

The binary decision threshold and the risk bands serve separate purposes:

| Probability | Prediction | Risk level |
|---|---|---|
| Below 0.40 | Unlikely to Churn | Low |
| 0.40 to below 0.60 | Likely to Churn | Medium |
| 0.60 or above | Likely to Churn | High |

## Project structure

```text
├── backend/          FastAPI routes, model service, validation and schemas
├── frontend/         React/Vite source and production build configuration
├── tests/            API and validation tests
├── Churn_predict.pkl Supplied trained pipeline (required at repository root)
├── Dockerfile        Multi-stage single-service image
├── requirements.txt  Python dependencies
└── README.md
```

## Local installation

Python 3.11 or 3.12 and Node.js 20 or newer are recommended. Place the supplied `Churn_predict.pkl` at the repository root before starting the API. The file is intentionally required; the service reports model loading failure rather than making substitute predictions.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm install
```

Run the backend in one terminal from the repository root:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Run the Vite development server in another terminal:

```powershell
cd frontend
npm run dev
```

Vite proxies `/api` to `http://localhost:8000`. For the production-style local app, build the frontend with `npm run build`, then start FastAPI; FastAPI serves the generated `frontend/dist` assets.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API and model loading status |
| GET | `/api/model-info` | Model schema, threshold and risk bands |
| POST | `/api/predict` | Validate and predict one customer (JSON) |
| POST | `/api/predict/bulk` | Validate an uploaded CSV and return enriched rows |

Single predictions return `Churn_Probability`, `Prediction` and `Risk_Level`. Bulk uploads use the multipart field `file`; input columns remain in the response with the three prediction columns appended.

Run the backend test suite with `pip install -r requirements-dev.txt` followed by `python -m pytest`.

## Render deployment

1. Push the repository, including the required model artifact, to the GitHub repository you intend to deploy.
2. In Render, create a **Web Service** from that repository and select **Docker** as the runtime.
3. Deploy the default branch. The Dockerfile builds the frontend, installs the backend and starts Uvicorn on `0.0.0.0` using Render's `PORT` value.

The application uses one service and no database. Individual and bulk prediction histories are stored in separate browser local storage keys and are specific to that browser. Existing mixed history is split by its recorded single or bulk row markers on first load. Render Free may spin down after inactivity, so the first request after idle time can take longer while the service starts.

## Future improvements

- Add persisted prediction history with a lightweight database if shared history is needed.
- Add model monitoring when verified churn outcomes become available.
- Improve accessibility and add automated release checks.
- Re-evaluate the model with new data and documented experiments before changing it.

## License

No license has been selected. Add a `LICENSE` file before redistributing this project under specific terms.
