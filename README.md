# AI Validation Risk Report Generator

This project is a Python-based tool that automates the process of generating risk assessment reports from software tool release notes. It leverages the Gemini AI platform to analyze the input data, identify potential risks, and create a structured risk assessment report in CSV format.

## Features

- **Automated Risk Assessment:** Utilizes Generative AI to perform risk analysis on release notes.
- **Multiple Preprocessors:** Supports different types of input files through a configurable preprocessing pipeline (e.g., generic AI processor, IAR Embedded Workbench specific processor).
- **Configurable:** All paths, model settings, and tool details are managed in a central `config.py` file.
- **Multiple Output Formats:** Generates a detailed risk report as a raw text file, a structured CSV, and a formatted XLSX spreadsheet.
- **Summarization:** Creates a high-level summary of the risk assessment.

### Prerequisites

- Python 3.8+
- An active Google AI Studio API key for Gemini.

### Dependencies

google-genai
python-dotenv

Then, install the dependencies using pip:

```bash
pip install -r google-genai python-dotenv
```

### Configure Environment Variables

Create a file named `.env` in the project's root directory. This file will store your secret API key.

```
API_KEY="YOUR_GEMINI_API_KEY"
```

Replace `"YOUR_GEMINI_API_KEY"` with your actual API key from Google AI Studio.

## Configuration

The main configuration for the project is located in `config.py`. Before running the application, you may need to adjust the following settings:

- **`TOOL_RELEASE_NOTES`**: Path to the input file containing the tool's release notes.
- **`TOOL_NAME`**, **`TOOL_VERSION_START`**, **`TOOL_VERSION_END`**: Information about the tool being validated.
- **`TOOL_PREPROCESSOR`**: The preprocessor to use. Set to `"AI"` for the general-purpose AI preprocessor or `"IAR_EmbeddedWorkbench"` for the specific IAR preprocessor.
- **Input/Output Paths**: The script uses various paths defined in `config.py` for reading instructions and writing output files. These are located in the `input/` and `output/` directories by default.

## Usage

To run the full risk assessment pipeline, execute the `main.py` script:

```bash
python main.py
```

The script will perform the following steps:
1.  Preprocess the release notes specified, either by AI or by custom automation script which is specified in `config.py`. The output is saved in `output/temp_output.txt`.
2.  Run the AI risk assessment engine to generate `output/final_risk_report.txt`.
3.  Generate a risk summary in `output/risk_summary_report.txt`.

After running the main script, you can convert the generated text report into a formatted `.xlsx` file by running the `csv_to_xlsx.py` script directly (currently not stable).

## Project Structure

```
AIValiReport/
├── .env                  # Environment variables (API Key)
├── config.py             # Main configuration file
├── main.py               # Main execution script
├── csv_to_xlsx.py        # Script to convert CSV output to XLSX
├── requirements.txt      # Project dependencies
├── AIProvider/           # Handles communication with the AI model
│   └── GeminiProvider.py
├── Preprocessor/      # Contains modules for preprocessing input data
│   ├── AIPreprocessor.py
│   └── IAREWPreprocessor.py
├── RiskAssessment/       # Contains the core risk assessment logic
│   ├── AIRiskAssessmentAgent.py
│   └── AIRiskSummary.py
├── input/                # Directory for input files (release notes, templates)
└── output/               # Directory for generated reports
```
