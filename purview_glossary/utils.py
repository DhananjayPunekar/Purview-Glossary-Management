import pandas as pd

def read_glossary_terms_from_excel(file_path):
    """
    Reads glossary terms from an Excel file and converts them to a list of dictionaries.

    Parameters:
    file_path (str): The path to the Excel file containing glossary terms.

    Returns:
    list: A list of dictionaries, where each dictionary represents a glossary term with keys for 'name', 'description', and other metadata.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.lower()
    return df.to_dict(orient='records')
