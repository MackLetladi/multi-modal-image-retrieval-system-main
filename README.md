# Multi-Modal Image Retrieval System

System for retrieving images using natural language queries. The system uses CLIP (Contrastive Language-Image Pre-Training) for multi-modal understanding and FAISS for efficient similarity search.

![Multi-Modal Image Retrieval System Overview](image.png)

## Features
- Natural language image search using OpenAI's CLIP model
- Efficient similarity search with Facebook AI's FAISS
- Modern React frontend with Material-UI
- FastAPI backend with async support

## System Architecture

```
├── backend/                 # Python backend
│   ├── requirements.txt     # Python dependencies
│   ├── src/
│   │   ├── api/             # FastAPI application
│   │   ├── data/            # Data loading and processing
│   │   ├── models/          # ML models and retrieval system
│   │   └── utils/           # Utility functions
│   └── tests/               # Backend tests
└── frontend/                # React frontend
    ├── public/
    ├── src/
    │   ├── components/      # React components
    │   ├── hooks/           # Custom React hooks
    │   ├── services/        # API services
    │   ├── styles/          # CSS styles
    │   └── utils/           # Utility functions
    └── package.json         # Frontend dependencies
```

## Assumptions

1. Cuda and all required libraries are installed
2. Using a sample of 500 images from the test_data_v2 folder
3. Images are in JPEG format
4. CLIP model is suitable for general image retrieval tasks
5. Users have basic familiarity with web interfaces
6. The Application was mainly tested on Windows but it should work on Linux
# Multi-Modal Image Retrieval System - Setup Guide  

This setup script works for both **Windows** and **Linux**.  

## 📂 1. Creating Necessary Folders  
- **Linux**: Create a folder in `$HOME` called `Image_retrieval`.  
- **Windows**: Create a folder in `%USERPROFILE%` called `Image_retrieval`.  

## 🔧 2. Checking and Installing Dependencies  

### ✅ Git  
- Check if Git is installed. If not, install it.  
- Clone the repository:  
  ```sh
  git clone https://github.com/MackLetladi/multi-modal-image-retrieval-system-main.git
  ```

### ✅ Anaconda  
- Check if Anaconda is installed. If not, download and install it from [Anaconda Website](https://www.anaconda.com/download).  

## 🌍 3. Creating a Virtual Environment  
- Create a virtual environment named `image_retrieval`. 
- - conda create --name image_retrieval python=3.11
- Activate the environment.
- - source activate image_retrieval


## ⚡ 4. Installing CUDA (For GPU Acceleration)  
- Download and install CUDA from the following link:  
  [CUDA Downloads](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local)  

## 🔥 5. Installing PyTorch  
- Run the following command in the env: image_retrieval
  ```sh
  pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
  ```

## 🔧 8. Installing Backend Dependencies  
- Navigate to the backend directory and install dependencies:  
  ```sh
  pip install -r backend/requirements.txt
  ```
- Ensure all dependencies are installed within the activated environment.  

---

# 🎨 Frontend Setup  

## 📂 1. Navigating to the Frontend Directory  
- Navigate to:  
  ```sh
  cd multi-modal-image-retrieval-system-main/frontend
  ```

## ✅ 2. Checking and Installing Node.js  
- Check if Node.js is installed. If not, install it from [Node.js Website](https://nodejs.org/).  

## 📦 3. Installing Frontend Dependencies  
- Run the following command:  
  ```sh
  npm install
  ```

---

# 🚀 Running the Application  

## 📥 1. Downloading the Dataset  
- Navigate to the dataset folder:  
  ```sh
  cd multi-modal-image-retrieval-system-main/backend/src/data
  ```
- Run the dataset download script:  
  ```sh
  python download_dataset.py
  ```
  _(This will download 500 datasets.)_  

## 🔥 2. Starting the Backend  
- Navigate to the API directory:  
  ```sh
  cd multi-modal-image-retrieval-system-main/backend/src/api
  ```
- Start the backend server:  
  ```sh
  python main.py
  ```

## 🎨 3. Starting the Frontend  
- Navigate to the frontend directory:  
  ```sh
  cd multi-modal-image-retrieval-system-main/frontend
  ```
- Start the frontend application:  
  ```sh
  npm start
  ```

---

This guide ensures your application runs smoothly on both **Windows** and **Linux**. 🚀
Once the backend and frontend is running, visit http://localhost:8000/ for the interactive API documentation.
