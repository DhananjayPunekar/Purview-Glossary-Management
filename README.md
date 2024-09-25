# Purview Glossary Management

This Python project is designed to manage Microsoft Purview glossary terms through its REST APIs. It allows you to add, retrieve, and delete glossary terms for a specific business domain by reading data from an Excel file.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Glossary Term Management](#glossary-term-management)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- **Retrieve Glossary Terms**: Fetch existing glossary terms from Microsoft Purview for a specific domain.
- **Add Glossary Terms**: Add new glossary terms by reading from an Excel sheet.
- **Delete Glossary Terms**: Delete existing glossary terms by their ID.
- **Domain Management**: Handles associating glossary terms with specific business domains in Microsoft Purview.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/purview-glossary-manager.git
   cd purview-glossary-manager
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows, use `venv\Scripts\activate`
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Excel file** containing the glossary terms to the project directory. The file should be in the format expected by the utility function in `purview_glossary/utils.py`.

## Configuration

Create a file named `config.py` in the root directory to store the configuration variables:

```python
# config.py

# Authentication details
tenant_id = 'your-tenant-id'
client_id = 'your-client-id'
client_secret = 'your-client-secret'
resource = 'https://purview.azure.net'

# Purview Account Name and Domain
purview_account_name = 'your-purview-account-name'
business_domain_guid = 'your-business-domain-guid'

# Excel file containing the glossary terms
glossary_excel_file = 'Enterprise-Glossary-Terms.xlsx'
```

Make sure you replace the placeholders (`your-tenant-id`, `your-client-id`, etc.) with your actual credentials.

## Usage

### Authentication

The authentication uses Azure's OAuth2.0 protocol. The client must have the **Data Steward** role assigned to the desired Purview domain. The authentication token is obtained by making a `POST` request to Azure’s token endpoint.

### Glossary Term Management

- **Adding Glossary Terms**: This is done by reading the glossary terms from an Excel file and adding them to Purview via the API.
- **Deleting Glossary Terms**: This can be done using the term’s unique ID, which can be retrieved via a GET request from Purview.

### Running the Application

To run the application and add glossary terms to Purview:

1. Ensure your `config.py` file is configured correctly.
2. Run the main script:
   ```bash
   python main.py
   ```

The script will authenticate and add the glossary terms from the specified Excel file to Microsoft Purview under the specified domain.

## Project Structure

```plaintext
purview-glossary-manager/
│
├── purview_glossary/          # Main package directory
│   ├── __init__.py            # Marks the package
│   ├── auth.py                # Handles authentication
│   ├── glossary.py            # Contains glossary-related API functions
│   ├── utils.py               # Utility functions (e.g., reading Excel files)
│
├── main.py                    # Main script to run the project
├── config.py                  # Configuration file for credentials and setup
├── requirements.txt           # List of required Python libraries
├── README.md                  # Project documentation (this file)
└── Enterprise-Glossary-Terms.xlsx  # Example glossary terms file (not included in repo)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
