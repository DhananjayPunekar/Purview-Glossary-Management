import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PurviewGlossaryManager:
    def __init__(self, token, tenant_id, headers):
        """
        Initializes the PurviewGlossaryManager with the required credentials and URLs.

        Parameters:
        token (str): The access token for authentication.
        tenant_id (str): The tenant ID used to construct Purview API URLs.
        headers (dict): The HTTP headers to include in API requests, containing the bearer token.
        """
        self.token = token
        self.tenant_id = tenant_id
        self.headers = headers
        self.base_url = f"https://{tenant_id}-api.purview-service.microsoft.com/datagovernance/catalog"
        logging.info(f"PurviewGlossaryManager initialized for tenant_id: {tenant_id}")

    def get_all_glossary_terms(self):
        """
        Fetches all glossary terms from Microsoft Purview.

        Returns:
        dict: The JSON response containing all glossary terms available in Purview.
        
        Raises:
        Exception: If the service principal does not have the required permissions (403 status code).
        """
        url = f"{self.base_url}/terms"
        logging.info("Fetching all glossary terms...")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 403:
            logging.error("Permission error while fetching glossary terms. Check Data Steward Role.")
            raise Exception("Permission error. Check Data Steward Role.")
        logging.info("Successfully fetched glossary terms.")
        return response.json()

    def get_all_domains(self):
        domains = {}
        url = f"{self.base_url}/businessdomains"
        logging.info("Fetching all governance domains...")
        response = requests.get(url, headers=self.headers)
        if response.status_code >= 400:
            logging.error("Permission error while fetching glossary terms. Check Data Steward Role.")
            raise Exception("Permission error. Check Data Steward Role.")
        for item in response.json()["value"]:
            domains[item["name"]] = item['id']
        return domains

    def get_term(self, term_id=None, term_name=None):
        """
        Fetches a glossary term from Microsoft Purview based on either term ID or term name.

        Args:
            term_id (str, optional): The unique identifier (GUID) of the glossary term.
            term_name (str, optional): The name of the glossary term.

        Returns:
            dict or list: If fetching by term_id, returns a dictionary with the term's details. 
                        If fetching by term_name, returns a list of terms that match the name.

        Raises:
            Exception: 
                - If both term_id and term_name are provided (only one should be used at a time).
                - If neither term_id nor term_name is provided.
                - If there is a permission issue (403 error) when fetching by term_id.
                - If no glossary term is found with the provided term_name.

        Notes:
            - If term_id is provided, it directly queries the API using the term's unique ID.
            - If term_name is provided, it searches the list of all glossary terms and returns matches.
            - Requires appropriate permissions to fetch terms (ensure the user has Data Steward Role).
        """
        # Check if both term_id and term_name are provided
        if term_id and term_name:
            raise Exception("Provide either 'term_id' or 'term_name', not both.")

        # Fetch by term_id
        if term_id:
            url = f"{self.base_url}/terms/{term_id}"
            logging.info(f"Fetching glossary term with ID: {term_id}...")
            response = requests.get(url, headers=self.headers)
            if response.status_code == 403:
                logging.error("Permission error while fetching glossary term. Check Data Steward Role.")
                raise Exception("Permission error. Check Data Steward Role.")
            logging.info(f"Successfully fetched glossary term [{term_id}].")
            return response.json()

        # Fetch by term_name
        elif term_name:
            logging.info(f"Fetching glossary term with name: {term_name}...")
            all_terms = self.get_all_glossary_terms()["value"]
            response = [term for term in all_terms if term["name"] == term_name]
            if response:
                logging.info(f"Successfully fetched glossary term [{term_name}].")
                return response
            else:
                raise Exception(f"The term [{term_name}] could not be found.")
        
        # Neither term_id nor term_name provided
        else:
            raise Exception("Either 'term_id' or 'term_name' must be provided.")

    def __check_term_exists(self, name, domain, all_terms, all_domains):
        """
        Checks whether a glossary term with the specified name already exists in the specified domain.

        Parameters:
        name (str): The name of the glossary term to check.
        domain (str): The name of the domain where the term should exist.
        all_terms (list): A list of existing glossary terms, where each term is represented as a dictionary with 'name' and 'domain' fields.
        all_domains (dict): A dictionary mapping domain names to their corresponding domain IDs.

        Workflow:
        - Iterates through the list of `all_terms`.
        - Compares the provided `name` and the domain's corresponding ID (retrieved from `all_domains`) with the existing terms.
        - If a match is found (i.e., both the term name and domain ID match), it returns `True` indicating the term already exists.
        - If no match is found after iterating through all terms, it returns `False`.

        Returns:
        bool: 
        - `True` if the term exists in the specified domain.
        - `False` if the term does not exist in the specified domain.
        """
        for item in all_terms:
            # Check if the term's name matches and if it exists in the same domain
            if item["name"] == name and item["domain"] == all_domains[domain]:
                return True
        
        # Return False if the term does not exist in the specified domain
        return False

    def upload_glossary_terms(self, terms):
        """
        Uploads a list of glossary terms to Microsoft Purview, ensuring that they are added to the correct domain 
        and checks for any existing terms before adding new ones.

        Parameters:
        terms (list): A list of dictionaries where each dictionary represents a glossary term, containing 'name', 'description', 'status', and 'domain'.

        Workflow:
        - Retrieves all existing glossary terms and domains using `get_all_glossary_terms()` and `get_all_domains()`.
        - Iterates through the provided list of terms.
        - For each term, logs the process of adding the term to the Purview glossary.
        - Calls the `__create_term` method to add the term, passing the term's details (name, description, status, domain), 
        along with the existing terms and domains to avoid duplicates and ensure correct domain assignment.

        Notes:
        - The `self.__create_term` method handles the actual creation of the glossary term and checks for duplicates.

        Returns:
        None
        """
        # Retrieve all existing glossary terms and domains
        all_terms = self.get_all_glossary_terms()["value"]
        all_domains = self.get_all_domains()
        
        # Add terms to Purview
        for term in terms:
            # Log the process of adding each term
            logging.info(f"Adding term: [{term['name']}]...")
            
            # Create the term in Purview, avoiding duplicates and ensuring proper domain association
            self.__create_term(term["name"], term["description"], term["status"], term["domain"], all_terms, all_domains)


    def __create_term(self, name, description, status, domain, all_terms, all_domains):
        """
        Adds a new glossary term to Microsoft Purview under a specific domain, if it does not already exist.

        Parameters:
        name (string): The glossary term name.
        description (string): The description of glossary term.
        status (string): Status of the glossary term. Can be `Draft` or `Published`.
        domain (string): Governance domain to which the glossary term should be added.
        all_terms (list): All existing glossary term retrieved by using `get_all_glossary_terms()`.
        all_domains (dict): A dictionary of domain name and domain guid retrieved by using `get_all_domains()`.

        Returns:
        dict: The API response confirming the creation of the glossary term.
        
        Raises:
        Exception: If the service principal does not have the required permissions (403 status code).
        """
        if self.__check_term_exists(name, domain, all_terms, all_domains):
            logging.info(f"The term [{name}] already exists in the governance domain [{domain}]. Hence skipping creating this term!")
            return None
        else:
            url = f"{self.base_url}/terms"
            term_payload = {
                "name": name,
                "description": description,
                "status": status,
                "domain": all_domains[domain]
            }
            logging.info(f"Creating glossary term: {name} under domain: {domain}")
            response = requests.post(url, json=term_payload, headers=self.headers)
            if response.status_code == 403:
                logging.warn(f"Permission error while creating term: [{name}]. Check permissions for governance domain [{domain}].")
                raise Exception(f"Permission error. Check Data Steward Role on governance domain [{domain}].")
            else:
                logging.info(f"Successfully created glossary term: [{name}] in the [{domain}] governance domain.")
            return response.json()

    def create_term(self, name, description, status, domain):
        """
        Adds a new glossary term to Microsoft Purview under a specific domain, if it does not already exist.

        Parameters:
        name (string): The glossary term name.
        description (string): The description of glossary term.
        status (string): Status of the glossary term. Can be `Draft` or `Published`.
        domain (string): Governance domain to which the glossary term should be added.

        Returns:
        dict: The API response confirming the creation of the glossary term.
        
        Raises:
        Exception: If the service principal does not have the required permissions (403 status code).
        """
        all_terms = self.get_all_glossary_terms()["value"]
        all_domains = self.get_all_domains()
        if self.__check_term_exists(name, domain, all_terms, all_domains):
            logging.info(f"The term [{name}] already exists in the governance domain [{domain}]. Hence skipping creating this term!")
            return None
        else:
            url = f"{self.base_url}/terms"
            term_payload = {
                "name": name,
                "description": description,
                "status": status,
                "domain": all_domains[domain]
            }
            logging.info(f"Creating glossary term: {name} under domain: {domain}")
            response = requests.post(url, json=term_payload, headers=self.headers)
            if response.status_code == 403:
                logging.warn(f"Permission error while creating term: [{name}]. Check permissions for governance domain [{domain}].")
                raise Exception(f"Permission error. Check Data Steward Role on governance domain [{domain}].")
            else:
                logging.info(f"Successfully created glossary term: [{name}] in the [{domain}] governance domain.")
            return response.json()

    def delete_glossary_term(self, term_id):
        """
        Deletes a specific glossary term from Microsoft Purview.

        Parameters:
        term_id (str): The unique identifier of the glossary term to delete.

        Returns:
        int: The status code of the DELETE request. 204 indicates success, 403 indicates a permission issue.
        """
        url = f"{self.base_url}/terms/{term_id}"
        logging.info(f"Deleting glossary term with id: {term_id}")
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            logging.info(f"Successfully deleted glossary term with id: {term_id}")
        elif response.status_code == 403:
            logging.warn(f"Permission error while deleting term with id: {term_id}. Check Data Steward Role.")
        return response.status_code

    def delete_all_glossary_term(self):
        """
        Deletes all glossary terms from Microsoft Purview.

        Workflow:
        - Retrieves all existing glossary terms using the `get_all_glossary_terms` method.
        - Iterates through the list of terms obtained from the response.
        - For each term, calls the `delete_glossary_term` method with the term's ID to delete it.
        - Checks the response status code for each delete operation:
            - If the status code is 204, it logs a message indicating the term was successfully deleted.
            - If the delete operation fails (i.e., the status code is not 204), it logs a warning message with the response status code.

        Returns:
        None
        """
        # Retrieve all existing glossary terms
        all_terms = self.get_all_glossary_terms()
        
        # Iterate through the list of terms and delete each one
        for term in all_terms["value"]:
            del_response = self.delete_glossary_term(term['id'])
            
            # Check the response status code to determine success or failure of deletion
            if del_response == 204:
                logging.info(f"[{term['name']}] has been deleted.")
            else:
                logging.warn(f"[{term['name']}] could not be deleted. Response status code: {del_response}")

