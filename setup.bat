@echo off

:: Check if CUDA is installed
where nvcc >nul 2>nul
if %errorlevel% neq 0 (
    echo CUDA is not installed. Please install CUDA from: https://developer.nvidia.com/cuda-downloads
    pause
    exit /b
)

:: Create Image_Retrieval folder
mkdir "%USERPROFILE%\Image_Retrieval"
cd "%USERPROFILE%\Image_Retrieval"

:: Check if Git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git from https://git-scm.com/
    pause
    exit /b
)

:: Clone the repository
git clone https://github.com/MackLetladi/multi-modal-image-retrieval-system-main.git

:: Check if Anaconda is installed
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Anaconda is not installed. Please install Anaconda from https://www.anaconda.com/products/distribution
    pause
    exit /b
)

:: Create and activate the environment
conda create -n image_retrieval python=3.9 -y
call conda activate image_retrieval

:: Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

:: Install backend dependencies
cd multi-modal-image-retrieval-system-main\backend
pip install -r requirements.txt

:: Download dataset
cd src\data
python download_dataset.py

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b
)

:: Install frontend dependencies
cd ..\frontend
npm install

:: Start the frontend server
start cmd /k "npm start"

:: Start the backend server
cd ..\backend\src\api
start cmd /k "python main.py"

echo Setup completed successfully!
pause