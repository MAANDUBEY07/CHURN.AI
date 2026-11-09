# CHURN.AI
A machine learning project that predicts customer churn using customer data. Includes a web dashboard for individual and bulk predictions, along with customer risk analysis.

# Customer Churn Prediction

A machine learning project that predicts whether a telecom customer is likely to leave a service. The project uses Logistic Regression and provides a web interface for making individual and bulk predictions.

## Features

- **Single Prediction:** Enter customer details to estimate their churn probability.
- **Bulk Prediction:** Upload a CSV file to generate predictions for multiple customers.
- **Risk Classification:** Categorizes customers into Low, Medium and High risk.
- **Analytics Dashboard:** View prediction summaries and customer risk distribution.
- **CSV Export:** Download prediction results for further analysis.
- **Input Validation:** Checks customer data before making predictions.

## Tech Stack

| Area | Technologies |
|---|---|
| Frontend | React, Tailwind CSS |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn, Pandas, NumPy |
| Charts | Recharts |
| Model | Logistic Regression |
| Deployment | Render |

## Machine Learning

The model was trained using the Telco Customer Churn dataset.

The training process included:
- Data cleaning and preprocessing
- Handling missing values
- Encoding categorical features
- Train-test splitting with stratification
- Hyperparameter tuning using GridSearchCV
- Model evaluation

The final model is a Scikit-learn pipeline containing preprocessing and Logistic Regression.

### Model Evaluation

| Metric | Score |
|---|---:|
| Accuracy | 78.39% |
| Precision (Churn) | 58% |
| Recall (Churn) | 68% |
| F1-score (Churn) | 63% |

*Evaluation results are based on the held-out test dataset.*

## Risk Classification

The application uses a probability threshold of 0.4 for its churn prediction.

| Churn Probability | Risk Level |
|---|---|
| Below 40% | Low |
| 40% – Below 60% | Medium |
| 60% and above | High |

## Project Structure

```text
churn-ai/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── model.py
│   ├── validation.py
│   └── Churn_predict.pkl
│
├── requirements.txt
├── Dockerfile
├── README.md
└── .gitignore
```

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd churn-ai
```

### 2. Set up the backend

```bash
python -m venv venv
```

Activate the environment:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn backend.main:app --reload
```

### 3. Set up the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend and backend will run locally on their configured development ports.

## Deployment

The application is deployed using Render.

[Live Demo](<deployment-url>)

## Future Improvements

- More detailed customer segmentation
- Additional machine learning models for comparison
- Improved customer-level insights
- Model performance monitoring

## License

This project is licensed under the MIT License.
