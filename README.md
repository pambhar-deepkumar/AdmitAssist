

# AdmitAssist

A Streamlit-based application for evaluating academic applications using AI-powered analysis and automated processing.

- [AdmitAssist](#admitassist)
  - [Setup Instructions](#setup-instructions)
    - [Overview](#overview)
    - [Setup Files](#setup-files)
      - [Installation Commands](#installation-commands)
    - [Secrets Configuration](#secrets-configuration)
  - [Demo Video](#demo-video)
  - [Frequently Asked Questions (FAQs)](#frequently-asked-questions-faqs)
  - [Troubleshooting Common Setup Issues](#troubleshooting-common-setup-issues)

## Setup Instructions

### Overview
- **Data Examples:**  
  The **data** folder contains several examples on which the app was tested. You can use these examples for your own experiments.

- **PDF Uploads:**  
  Uploading PDF files is supported. However, converting them with Docling may take some time—especially on PCs without GPUs. If conversion is slow, use the pre-converted PDFs found in the examples folder.

### Setup Files

The repository provides two types of setup files for each operating system:

- **Linux/Mac:**  
  Provided as `.sh` files.

- **Windows:**  
  Provided as `.bat` files.

There are two setup scripts:

- **setup:**  
  Sets up the basic virtual environment and installs all necessary dependencies.
  
- **setup_dev:**  
  Performs all actions of **setup** and, additionally, configures the development environment; this includes installing pre-commit hooks, linters, and formatters.

**Which script to use:**

- Use **setup** if you only intend to run the application.
- Use **setup_dev** if you plan to modify the code or contribute to development.

#### Installation Commands

**For Linux/Mac:**

*Basic setup:*
```bash
chmod +x setup.sh
./setup.sh
```

*Development setup:*
```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

**For Windows:**

*Basic setup:*
```bat
setup.bat
```

*Development setup:*
```bat
setup_dev.bat
```

### Secrets Configuration

The app requires a secrets file for Streamlit to automatically load your API keys. A sample file is provided at `.streamlit/sample-secrets.toml`. 

**Instructions:**
- Rename `.streamlit/sample-secrets.toml` to `.streamlit/secrets.toml`.
- Replace the placeholder key with your actual API key.

Using a secrets file in this manner separates sensitive data from code, following security best practices.

## Demo Video

Below is an embedded demo video showcasing the app in action:

<video controls>
  <source src="demo/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

If the video does not appear please click [here](demo/demo.mp4)
## Frequently Asked Questions (FAQs)

- **What example data can I use?**  
  The **data** folder contains several examples that were used during testing. These can be directly utilized in your workflow.

- **How does the PDF upload work?**  
  The app supports PDF uploads; however, PDF conversion using Docling can be slow on PCs without GPUs. If you encounter delays, consider using the converted PDFs available in the examples folder.

- **Which setup script should I choose?**  
  - Use **setup** for a basic installation that gets the app running.
  - Use **setup_dev** for development work, as it installs additional tools like pre-commit hooks, linters, and formatters.

- **Why do I need to configure a secrets file?**  
  The secrets file allows Streamlit to load API keys securely. This practice avoids hardcoding sensitive information in your code, thereby improving overall security.

- **What to do about Docling installation issues on Apple Silicone?**  
  Users have reported problems with Docling on Apple Silicon. Consider checking the project's issue tracker or community forums for updated workarounds if you experience these errors.

## Troubleshooting Common Setup Issues

- Ensure you have Python 3.8 or higher installed.
- Verify that you have the necessary permissions to execute the setup files.
- If dependency installation fails, try running the commands manually within your virtual environment.
- For pre-commit hook issues in development mode, run:
  ```bash
  pre-commit run --all-files
  ```
  to diagnose and fix formatting or linting problems.
- For Apple Silicone-specific Docling issues, monitor the issue tracker for resolutions or alternative installation methods.

---
