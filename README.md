# Heavy Machinery Copilot - AWS Bedrock Knowledge Base with Aurora Serverless

🛠️ **Live Application:** [https://intelligent-document-queriyng-system.streamlit.app/](https://intelligent-document-queriyng-system.streamlit.app/)

This project is an intelligent document querying system that uses AWS Bedrock Knowledge Base integrated with an Aurora Serverless PostgreSQL database. It features a Streamlit chat application that allows users to query heavy machinery documentation using natural language.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Live Application](#live-application)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Streamlit Application](#streamlit-application)
6. [Deployment Steps](#deployment-steps)
7. [Running the Application Locally](#running-the-application-locally)
8. [Using the Scripts](#using-the-scripts)
9. [Troubleshooting](#troubleshooting)

## Project Overview

This project is a RAG (Retrieval-Augmented Generation) system that enables natural language queries over heavy machinery documentation. It consists of:

### Infrastructure Components

1. **Stack 1** - Terraform configuration for creating:
   - A VPC
   - An Aurora Serverless PostgreSQL cluster
   - S3 Bucket to hold documents
   - Necessary IAM roles and policies

2. **Stack 2** - Terraform configuration for creating:
   - A Bedrock Knowledge Base
   - Necessary IAM roles and policies

3. **Database Setup** - SQL queries to prepare the Postgres database for vector storage
4. **S3 Upload Script** - Python script for uploading files to S3

### Application Components

1. **Streamlit Chat Application** (`app.py`) - Interactive web interface for querying the knowledge base
2. **Bedrock Utilities** (`bedrock_utils.py`) - Core functions for:
   - Prompt validation and categorization
   - Knowledge base querying
   - LLM response generation
   - Source formatting

The system allows users to ask questions about heavy machinery (excavators, bulldozers, loaders, etc.) and receive accurate answers based on the documentation stored in the knowledge base.

## Live Application

🌐 **Access the live application:** [https://intelligent-document-queriyng-system.streamlit.app/](https://intelligent-document-queriyng-system.streamlit.app/)

The application is deployed on Streamlit Cloud and provides:

- Interactive chat interface for querying heavy machinery documentation
- Configurable LLM models (Claude 3 Haiku, Sonnet, and 3.5 variants)
- Adjustable temperature and top_p parameters for response control
- Source citations with confidence scores
- Prompt validation to ensure queries are relevant and appropriate

## Prerequisites

Before you begin, ensure you have the following:

- AWS CLI installed and configured with appropriate credentials
- Terraform installed (version 0.12 or later)
- Python 3.10 or later
- pip (Python package manager)

## Project Structure

```text
project-root/
│
├── app.py                          # Streamlit chat application
├── bedrock_utils.py                # Core Bedrock functions (KB query, LLM, validation)
├── requirements.txt                # Python dependencies
│
├── stack1/                         # Infrastructure Stack 1 (VPC, Aurora, S3)
|   ├── main.tf
|   ├── outputs.tf
|   └── variables.tf
|
├── stack2/                         # Infrastructure Stack 2 (Bedrock KB)
|   ├── main.tf
|   ├── outputs.tf
|   └── variables.tf
|
├── modules/
│   ├── aurora_serverless/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── bedrock_kb/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── scripts/
│   ├── aurora_sql.sql              # Database setup queries
│   └── upload_to_s3.py             # S3 file upload script
│
├── spec-sheets/                    # Document storage (PDFs)
│   └── machine_files.pdf
│
├── .streamlit/
│   └── secrets.toml                 # AWS credentials (not in repo)
│
└── README.md
```

## Deployment Steps

1. Clone this repository to your local machine.

2. Navigate to the project Stack 1. This stack includes VPC, Aurora servlerless and S3

3. Initialize Terraform:

   ```bash
   terraform init
   ```

4. Review and modify the Terraform variables in `main.tf` as needed, particularly:
   - AWS region
   - VPC CIDR block
   - Aurora Serverless configuration
   - s3 bucket

5. Deploy the infrastructure:

   ```bash
   terraform apply
   ```

   Review the planned changes and type "yes" to confirm.

6. After the Terraform deployment is complete, note the outputs, particularly the Aurora cluster endpoint.

7. Prepare the Aurora Postgres database. This is done by running the sql queries in the script/ folder. This can be done through Amazon RDS console and the Query Editor.

8. Navigate to the project Stack 2. This stack includes Bedrock Knowledgebase

9. Initialize Terraform:

   ```bash
   terraform init
   ```

10. Use the values outputs of the stack 1 to modify the values in `main.tf` as needed:
     - Bedrock Knowledgebase configuration

11. Deploy the infrastructure:

    ```bash
    terraform apply
    ```

    Review the planned changes and type "yes" to confirm.

12. Upload pdf files to S3, place your files in the `spec-sheets` folder and run:

    ```bash
    python scripts/upload_to_s3.py
    ```

    Make sure to update the S3 bucket name in the script before running.

13. Sync the data source in the knowledgebase to make it available to the LLM.

## Streamlit Application

### Features

The Streamlit application (`app.py`) provides an interactive chat interface with the following features:

- **Multi-Model Support**: Choose from Claude 3 Haiku, Sonnet, and 3.5 variants
- **Configurable Parameters**:
  - Temperature (0.0-1.0): Controls creativity and randomness
  - Top_P (0.0-1.0): Controls word choice variety
  - Min Prompt Length: Rejects queries that are too short
  - Number of KB Results: Adjusts context retrieval (1-10)
  - Max Response Tokens: Controls response length (100-1000)
- **Prompt Validation**: Automatically categorizes and validates user prompts to ensure:
  - Queries are relevant to heavy machinery
  - No prompt injection attempts
  - No toxic or inappropriate content
  - No off-topic requests
- **Source Citations**: Displays source documents with confidence scores
- **Knowledge Base Validation**: Validates KB ID before processing queries

### Application Functions

The `bedrock_utils.py` module contains:

- `valid_prompt()`: Validates and categorizes user prompts using LLM classification
- `query_knowledge_base()`: Retrieves relevant context from the Bedrock Knowledge Base
- `generate_response()`: Generates LLM responses using retrieved context
- `is_valid_kb_id()`: Validates Knowledge Base ID
- `format_sources()`: Formats retrieval results for display

## Running the Application Locally

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials**:

   Create a `.streamlit/secrets.toml` file with your AWS credentials:

   ```toml
   [aws]
   aws_access_key_id = "your-access-key"
   aws_secret_access_key = "your-secret-key"
   region = "your-region"
   ```

3. **Run the Streamlit app**:

   ```bash
   streamlit run app.py
   ```

4. **Access the application**:
   Open your browser to `http://localhost:8501`

## Using the Scripts

### S3 Upload Script

The `upload_to_s3.py` script does the following:

- Uploads all files from the `spec-sheets` folder to a specified S3 bucket
- Maintains the folder structure in S3

To use it:

1. Update the `bucket_name` variable in the script with your S3 bucket name.
2. Optionally, update the `prefix` variable if you want to upload to a specific path in the bucket.
3. Run `python scripts/upload_to_s3.py`.

## Troubleshooting

- If you encounter permissions issues, ensure your AWS credentials have the necessary permissions for creating all the resources.
- For database connection issues, check that the security group allows incoming connections on port 5432 from your IP address.
- If S3 uploads fail, verify that your AWS credentials have permission to write to the specified bucket.
- For any Terraform errors, ensure you're using a compatible version and that all module sources are correctly specified.

For more detailed troubleshooting, refer to the error messages and logs provided by Terraform and the Python scripts.
