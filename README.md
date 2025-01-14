
# Application Evaluation SystemP
- [Application Evaluation SystemP](#application-evaluation-systemp)
  - [System Overview](#system-overview)
    - [Key Components](#key-components)
      - [1. File Management (`modules/file_handler.py`)](#1-file-management-modulesfile_handlerpy)
      - [2. UI Components (`modules/ui_components.py`)](#2-ui-components-modulesui_componentspy)
      - [3. Evaluation Strategies (`evaluation_strategies/`)](#3-evaluation-strategies-evaluation_strategies)
      - [4. LLM Management (`utils/llm_manager.py`)](#4-llm-management-utilsllm_managerpy)
      - [5. Document Processing (`utils/document_processor.py`)](#5-document-processing-utilsdocument_processorpy)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Option 1: Using pip and venv](#option-1-using-pip-and-venv)
    - [Option 2: Using Conda](#option-2-using-conda)
  - [Configuration](#configuration)
    - [1. Environment Setup](#1-environment-setup)
    - [2. File Upload Configuration](#2-file-upload-configuration)
    - [3. LLM Configuration](#3-llm-configuration)
  - [Running the Application](#running-the-application)
  - [Project Structure](#project-structure)
  - [Adding New Features](#adding-new-features)
    - [New Evaluation Strategy](#new-evaluation-strategy)
    - [New Document Type](#new-document-type)
  - [Testing](#testing)
  - [Contributing](#contributing)
  - [License](#license)
  - [Support](#support)



A Streamlit-based application for evaluating academic applications using AI-powered analysis and automated processing.

## System Overview

### Key Components

#### 1. File Management (`modules/file_handler.py`)
- Handles document uploads and validation
- Configurable through upload_config.yaml
- Acts as the initial validation layer

#### 2. UI Components (`modules/ui_components.py`)
- Manages Streamlit interface
- Handles user interactions
- Displays progress and results

#### 3. Evaluation Strategies (`evaluation_strategies/`)
Different approaches for application evaluation:
- Academic Focus Strategy
- Research Potential Strategy
- Comprehensive Evaluation Strategy

#### 4. LLM Management (`utils/llm_manager.py`)
- Manages AI model usage
- Optimizes model selection based on tasks
- Cost-effective resource utilization

#### 5. Document Processing (`utils/document_processor.py`)
- Extracts information from documents
- Prepares data for evaluation
- Handles different document formats

## Features
- Multiple evaluation strategies
- Smart AI model utilization
- Progress tracking
- Automated report generation
- Modular architecture

## Prerequisites
- Python 3.8 or higher
- Git
- OpenAI API key

## Installation

### Option 1: Using pip and venv

1. Clone the repository:
```bash
git clone https://github.com/yourusername/application-evaluation-system.git
cd application-evaluation-system
```

2. Create and activate virtual environment:

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

### Option 2: Using Conda

1. Clone the repository:
```bash
git clone https://github.com/yourusername/application-evaluation-system.git
cd application-evaluation-system
```

2. Create and activate conda environment:
```bash
conda create -n app_eval python=3.8
conda activate app_eval
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Environment Setup
Create a `.env` file:
```env
OPENAI_API_KEY=your_api_key_here
```

### 2. File Upload Configuration
In `config/upload_config.yaml`:
```yaml
file_inputs:
  - name: curriculum_analysis
    display_name: "Curriculum Analysis"
    required: true
    allowed_extensions: [".xlsx", ".xls"]
```

### 3. LLM Configuration
In `config/llm_config.yaml`:
```yaml
models:
  gpt4:
    name: "gpt-4"
    use_for: ["final_evaluation"]
  gpt35:
    name: "gpt-3.5-turbo"
    use_for: ["initial_screening"]
```

## Running the Application

1. Activate your environment:
```bash
# venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# or conda
conda activate app_eval
```

2. Start the application:
```bash
cd app
streamlit run main.py
```

3. Access at `http://localhost:8501`

## Project Structure
```
application_evaluation_system/
├── app/
│   ├── main.py                    # Main application
│   ├── config/                    # Configuration files
│   ├── modules/                   # Core modules
│   ├── evaluation_strategies/     # Evaluation implementations
│   └── utils/                     # Utility functions
├── tests/                         # Test suite
├── requirements.txt               # Dependencies
└── README.md                      # Documentation
```

## Adding New Features

### New Evaluation Strategy
1. Create new class in `evaluation_strategies/`
2. Inherit from `BaseEvaluationStrategy`
3. Implement evaluation logic
4. Register in processor

### New Document Type
1. Update `upload_config.yaml`
2. Add processing logic
3. Update validation rules

## Testing
```bash
# Run tests
python -m pytest tests/
```

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License
MIT License - see LICENSE file

## Support
- Create an issue for bugs
- Submit feature requests through issues
- Check documentation for common questions

This project emphasizes:
- Modular design
- Flexible evaluation strategies
- Efficient resource usage
- Easy maintenance
- Clear documentation