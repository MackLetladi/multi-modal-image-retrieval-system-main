#!/bin/bash

# Check if CUDA is installed
if ! command -v nvcc &> /dev/null; then
    echo "CUDA is not installed. Please install CUDA from: https://developer.nvidia.com/cuda-downloads"
    exit 1
fi

# Create Image_Retrieval folder
mkdir -p $HOME/Image_Retrieval
cd $HOME/Image_Retrieval

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Installing Git..."
    sudo apt-get update
    sudo apt-get install -y git
fi

# Clone the repository
git clone https://github.com/MackLetladi/multi-modal-image-retrieval-system-main.git

# Check if Anaconda is installed
if ! command -v conda &> /dev/null; then
    echo "Anaconda is not installed. Installing Anaconda..."
    wget https://repo.anaconda.com/archive/Anaconda3-latest-Linux-x86_64.sh
    bash Anaconda3-latest-Linux-x86_64.sh -b -p $HOME/anaconda
    export PATH="$HOME/anaconda/bin:$PATH"
    conda init bash
    source ~/.bashrc
fi

# Create and activate the environment
conda create -n image_retrieval python=3.9 -y
conda activate image_retrieval

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install backend dependencies
cd multi-modal-image-retrieval-system-main/backend
pip install -r requirements.txt

# Download dataset
cd src/data
python download_dataset.py

# Install Node.js for frontend
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install frontend dependencies
cd ../frontend
npm install

# Start the frontend server
npm start &

# Start the backend server
cd ../backend/src/api
python main.py

echo "Setup completed successfully!"