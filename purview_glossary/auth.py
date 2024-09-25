import requests

def get_purview_token(tenant_id, client_id, client_secret, resource):
    """
    Obtains an authentication token for Microsoft Purview using client credentials.

    Parameters:
    tenant_id (str): The tenant ID of the Azure Active Directory.
    client_id (str): The client ID (application ID) of the registered app.
    client_secret (str): The client secret (application key) for the registered app.
    resource (str): The resource for which the token is requested (Purview API).

    Returns:
    str: The access token required for making API requests to Purview.
    """
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': resource
    }
    response = requests.post(url, data=payload)
    return response.json().get('access_token')
