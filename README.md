# Multi-Modal Image Retrieval System

A production-ready system for retrieving images using natural language queries. The system uses CLIP (Contrastive Language-Image Pre-Training) for multi-modal understanding and FAISS for efficient similarity search.

## Features

- Natural language image search using OpenAI's CLIP model
- Efficient similarity search with Facebook AI's FAISS
- Modern React frontend with Material-UI
- Accessibility features including:
  - High contrast mode
  - Adjustable font size
  - Screen reader support
  - Voice search capability
- FastAPI backend with async support
- Comprehensive error handling
- Production-ready code structure

## System Architecture

```
├── backend/                 # Python backend
│   ├── requirements.txt    # Python dependencies
│   ├── src/
│   │   ├── api/           # FastAPI application
│   │   ├── data/          # Data loading and processing
│   │   ├── models/        # ML models and retrieval system
│   │   └── utils/         # Utility functions
│   └── tests/             # Backend tests
└── frontend/              # React frontend
    ├── public/
    ├── src/
    │   ├── components/    # React components
    │   ├── services/      # API services
    │   └── styles/        # CSS styles
    └── package.json       # Frontend dependencies
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+
- 500 test images from the AI vs. Human-Generated dataset

## Installation

1. Clone the repository:
\`\`\`bash
git clone https://github.com/yourusername/multimodal-retrieval.git
cd multimodal-retrieval
\`\`\`

2. Set up the backend:
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

3. Set up the frontend:
\`\`\`bash
cd frontend
npm install
\`\`\`

4. Create a .env file in the backend directory:
\`\`\`
IMAGE_DATA_DIR=/path/to/your/images
\`\`\`

## Running the Application

1. Start the backend server:
\`\`\`bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.api.main:app --reload
\`\`\`

2. Start the frontend development server:
\`\`\`bash
cd frontend
npm start
\`\`\`

3. Open your browser and navigate to http://localhost:3000

## Running Tests

Backend tests:
\`\`\`bash
cd backend
pytest
\`\`\`

Frontend tests:
\`\`\`bash
cd frontend
npm test
\`\`\`

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for the interactive API documentation.

## Assumptions

1. Using a sample of 500 images from the test_data_v2 folder
2. Images are in JPEG format
3. CLIP model is suitable for general image retrieval tasks
4. Users have basic familiarity with web interfaces

## Production Deployment Considerations

1. Use production-grade WSGI server (e.g., Gunicorn) for the backend
2. Set up proper SSL/TLS certificates
3. Implement rate limiting and authentication
4. Use environment variables for configuration
5. Set up monitoring and logging
6. Configure proper CORS settings
7. Optimize the FAISS index for production load

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT

## Acknowledgments

- OpenAI for the CLIP model
- Facebook Research for FAISS
- The creators of the AI vs. Human-Generated dataset


## BackEnd
-install Conda
-Install Pycharm or any IDE of your choice
-install conda
-create an environment variable
-open a terminal and use the following command: conda create --name myenv python=3.11
-In the IDE make sure that you selected the newly created interpreter
-Install Cuda from the following link we used CUDA 12: https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local
-Install PyTorch: pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
-pip install -r requirements.txt
-Make Sure the enviroment is properl activated: Windows: activate "name" Unix: source activate "name"
-python download_dataset.py
-cd to the folder backend make sure the right environment is activated: run the following commands: make sure you are in the correct folder :Python main 


## FrontEnd
-cd to the folder frontend: run the following commands:
-npm install
-npm run start