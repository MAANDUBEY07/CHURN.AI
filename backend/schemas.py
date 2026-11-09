from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

YesNo = Literal["Yes", "No"]
class CustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    SeniorCitizen: Literal[0, 1]
    tenure: float = Field(ge=0, le=72)
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float = Field(ge=0)
    gender: Literal["Male", "Female"]
    Partner: YesNo
    Dependents: YesNo
    PhoneService: YesNo
    MultipleLines: Literal["Yes", "No", "No phone service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: Literal["Yes", "No", "No internet service"]
    OnlineBackup: Literal["Yes", "No", "No internet service"]
    DeviceProtection: Literal["Yes", "No", "No internet service"]
    TechSupport: Literal["Yes", "No", "No internet service"]
    StreamingTV: Literal["Yes", "No", "No internet service"]
    StreamingMovies: Literal["Yes", "No", "No internet service"]
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: YesNo
    PaymentMethod: Literal["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
