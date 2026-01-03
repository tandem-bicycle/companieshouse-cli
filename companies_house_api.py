
import requests
import os

class CompaniesHouseAPI:
    """
    A Python wrapper for the UK Companies House API.
    """
    
    BASE_URL = "https://api.companieshouse.gov.uk"

    def __init__(self, api_key=None):
        """
        Initializes the API client.
        
        Args:
            api_key (str, optional): Your Companies House API key. 
                                     If not provided, it will try to use the 
                                     COMPANIES_HOUSE_API_KEY environment variable.
        
        Raises:
            ValueError: If the API key is not provided or found.
        """
        self.api_key = api_key or os.getenv("COMPANIES_HOUSE_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please provide it or set the COMPANIES_HOUSE_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def _make_request(self, endpoint):
        """
        Internal method to handle API requests.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}{endpoint}")
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"A request error occurred: {req_err}")
        return None

    def search_companies(self, query):
        """
        Searches for companies by name.
        
        Args:
            query (str): The search term.
            
        Returns:
            dict: The JSON response from the API, or None if an error occurred.
        """
        return self._make_request(f"/search/companies?q={query}")

    def get_company_profile(self, company_number):
        """
        Retrieves the profile for a specific company.
        
        Args:
            company_number (str): The company registration number.
            
        Returns:
            dict: The JSON response from the API, or None if an error occurred.
        """
        return self._make_request(f"/company/{company_number}")

    def get_persons_with_significant_control(self, company_number):
        """
        Retrieves the Persons with Significant Control for a specific company.
        
        Args:
            company_number (str): The company registration number.
            
        Returns:
            dict: The JSON response from the API, or None if an error occurred.
        """
        return self._make_request(f"/company/{company_number}/persons-with-significant-control")

    def get_filing_history(self, company_number, items_per_page=100):
        """
        Retrieves filing history items for a specific company.
        
        Args:
            company_number (str): The company registration number.
            items_per_page (int): Number of items to retrieve per page. Defaults to 100.
            
        Returns:
            dict: The JSON response from the API, or None if an error occurred.
        """
        return self._make_request(f"/company/{company_number}/filing-history?items_per_page={items_per_page}")

