import pandas as pd
# from langchain_core.documents import Document

def documents_to_dataframe(documents):
    # Create a list to hold the extracted data
    data = []
    
    # Iterate over each Document in the list
    for doc in documents:
        # Extract metadata and content
        metadata = doc.metadata
        content = doc.page_content
        
        # Append the extracted information as a dictionary
        data.append({
            "Title": metadata.get('title', ''),
            "Description": metadata.get('description', ''),
            "Source": metadata.get('source', ''),
            "Language": metadata.get('language', ''),
            "Content": content
        })
    
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data)
    return df