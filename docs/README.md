Here’s a comprehensive `README.md` file for your EvidenceAI project:

---

# EvidenceAI

EvidenceAI is a modular system designed to process unstructured legal data and transform it into actionable insights. Using the A-Team framework (Librarian, Detective, Organizer, Oracle), EvidenceAI helps users organize, analyze, and generate meaningful reports from legal documents.

## Table of Contents
1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Key Components](#key-components)
4. [Setup Instructions](#setup-instructions)
5. [Usage Guide](#usage-guide)
6. [Features and Modules](#features-and-modules)
7. [Next Steps](#next-steps)

---

## Overview
EvidenceAI provides a structured workflow for analyzing legal documents, focusing on:
- **PDF Parsing**: Extracting text and metadata from documents.
- **Threading**: Identifying relationships across files (Pending).
- **Relationship Analysis**: Mapping connections between entities (Pending).
- **Topic Detection**: Extracting themes from the data (Pending).

The system saves progress at every step using checkpoints, allowing for incremental development and debugging.

---

## Directory Structure
```plaintext
/project_root
|-- /src
|   |-- message_parser.py         # Handles document parsing and metadata extraction
|   |-- parser.py                 # Coordinates the analysis pipeline
|   |-- test_processor.py         # Validates pipeline functionality
|
|-- /input                        # Folder for raw input data (PDFs, emails, etc.)
|-- /output                       # Folder for generated results and reports
|-- /dev_checkpoints              # Stores checkpoints for resuming sessions
|
|-- README.md                     # Project documentation (this file)
|-- requirements.txt              # Python dependencies
|-- run_analysis.bat              # Batch file for running the analysis pipeline
|-- start_session.bat             # Batch file for initializing a session
```

---

## Key Components
### `message_parser.py`
- **Purpose**: Parse documents, extract text, identify entities and topics.
- **Input**: Raw files from `/input`.
- **Output**: Extracted metadata saved to structured formats.

### `parser.py`
- **Purpose**: Orchestrates the analysis pipeline, integrating various modules.
- **Input**: Outputs from `message_parser.py`.
- **Output**: Processed data for further analysis or reporting.

### `test_processor.py`
- **Purpose**: End-to-end testing and validation of the system.
- **Input**: Sample input data.
- **Output**: Test results and error logs.

---

## Setup Instructions

### 1. Prerequisites
Ensure the following software is installed:
- Python 3.8 or higher
- Required Python libraries (see `requirements.txt`)

### 2. Install Dependencies
Run the following command in your terminal to install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Prepare Directories
Ensure the following folders exist:
- `/input` for raw files (PDFs, etc.)
- `/output` for storing results
- `/dev_checkpoints` for saving session progress

---

## Usage Guide

### Start an Analysis Session
1. Run the `start_session.bat` file to initialize the session.
2. Choose from the available options:
   - **1**: Start the analysis pipeline.
   - **2**: View project status only.
   - **3**: Exit the session.

### Run the Pipeline
1. Use `run_analysis.bat` to process files in `/input`.
2. Check the `/output` folder for results.

### Test the System
1. Use `test_processor.py` to validate the pipeline with sample data:
   ```bash
   python src/test_processor.py
   ```

---

## Features and Modules

### Current Features
- **PDF Parsing**: Completed.
- **Checkpointing**: Saves progress after each module.
- **Modular Design**: Allows incremental development and testing.

### Pending Features
- **Threading Module**: Analyze document relationships.
- **Relationship Analysis**: Map connections between entities.
- **Topic Detection**: Extract thematic insights.

---

## Next Steps
- Implement the pending modules (Threading, Relationship Analysis, Topic Detection).
- Enhance error handling and logging mechanisms.
- Extend parsing capabilities to support non-PDF formats.
- Improve automation for report generation.

---

## Support
If you encounter issues or have questions, please contact the project team or submit a pull request for any enhancements.

---

This `README.md` provides a comprehensive overview of the project and serves as a guide for onboarding new contributors or revisiting the project later. Let me know if you'd like adjustments or additional sections!