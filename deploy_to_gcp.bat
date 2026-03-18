@echo off
echo [ShiftOps-OS] Preparing GCP Native Deployment...

:: Check for gcloud
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: gcloud CLI not found. Please install it first.
    exit /b 1
)

:: Get Project ID
for /f "tokens=*" %%i in ('gcloud config get-value project') do set PROJECT_ID=%%i

if "%PROJECT_ID%"=="" (
    echo Error: No GCP project selected. Run 'gcloud config set project PROJECT_ID'
    exit /b 1
)

echo Target Project: %PROJECT_ID%
echo.
echo [1/2] Enabling required GCP APIs...
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com

echo [2/2] Submitting build to Google Cloud Build...
gcloud builds submit --config ShiftOps-OS/infrastructure/gcp/cloudbuild.yaml

echo.
echo Deployment triggered. Check the Google Cloud Console for progress.
