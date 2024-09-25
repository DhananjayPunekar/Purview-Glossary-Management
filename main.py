import logging
from purview_glossary.auth import get_purview_token
from purview_glossary.glossary import PurviewGlossaryManager
from purview_glossary.utils import read_glossary_terms_from_excel
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Get authentication token
    logging.info("Attempting to get Purview token...")
    token = get_purview_token(config.tenant_id, config.client_id, config.client_secret, config.resource)
    logging.info("Successfully obtained Purview token.")

    # Set up headers with the token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Initialize glossary manager
    logging.info("Initializing PurviewGlossaryManager...")
    glossary_manager = PurviewGlossaryManager(token, config.tenant_id, headers)
    logging.info("PurviewGlossaryManager initialized successfully.")

    # Read glossary terms from Excel
    logging.info("Reading glossary terms from Excel...")
    glossary_terms = read_glossary_terms_from_excel('Enterprise-Glossary-Terms.xlsx')
    logging.info(f"Successfully read {len(glossary_terms)} glossary terms from Excel.")

    glossary_manager.upload_glossary_terms(glossary_terms)

except Exception as e:
    logging.error(f"An error occurred: {str(e)}")
