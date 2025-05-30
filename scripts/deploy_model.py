from dotenv import load_dotenv
load_dotenv() 
import os
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Environment,
    CodeConfiguration
)

# Initialize ML client
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AZURE_ML_WORKSPACE"]
)

# Create or update the endpoint
endpoint = ManagedOnlineEndpoint(
    name="stock-predict-endpoint",
    description="Stock price prediction (model + scaler)",
    auth_mode="key"
)
ml_client.begin_create_or_update(endpoint).wait()

# Define the inference environment
env = Environment(
    name="stock-inference-env",
    image="mcr.microsoft.com/azureml/minimal-ubuntu20.04-py38-cpu-inference:latest",
    conda_file="environment.yml",
)

# Deploy the latest registered model (bundle of model + scaler)
deployment = ManagedOnlineDeployment(
    name="default",
    endpoint_name=endpoint.name,
    model=f"{os.environ['MODEL_NAME']}:latest",
    environment=env,
    code_configuration=CodeConfiguration(
        code="./src/endpoint",
        scoring_script="score.py"
    ),
    instance_type="Standard_DS2_v2",
    instance_count=1
)
ml_client.begin_create_or_update(deployment).wait()
ml_client.online_endpoints.begin_start(endpoint.name).result()
print(f"Deployed endpoint '{endpoint.name}'")