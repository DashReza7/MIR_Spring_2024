from .index_reader import Index_reader
from .indexes_enum import Indexes, Index_types
import json
import os

class Metadata_index:
    def __init__(self, path):
        """
        Initializes the Metadata_index.

        Parameters
        ----------
        path : str
            The path to the indexes.
        """
        self.path = path
        with open(path + "genres_document_length_index.json", "r") as file:
            data = json.load(file)
            self.len_documents = len(data)
        self.metadata_index = self.create_metadata_index()

    def create_metadata_index(self):    
        """
        Creates the metadata index.
        """
        metadata_index = {}
        metadata_index['averge_document_length'] = {
            'stars': self.get_average_document_field_length('stars'),
            'genres': self.get_average_document_field_length('genres'),
            'summaries': self.get_average_document_field_length('summaries')
        }
        metadata_index['document_count'] = self.len_documents
        return metadata_index
    
    def get_average_document_field_length(self, where):
        """
        Returns the sum (corrected: average) of the field lengths of all documents in the index.

        Parameters
        ----------
        where : str
            The field to get the document lengths for.
        """
        path = self.path + where + "_document_length_index.json"
        docID_docLen = None
        with open(path, "r") as file:
            docID_docLen = json.load(file)
        sum = 0
        for val in docID_docLen.values():
            sum += val
        return sum / len(docID_docLen)        

    def store_metadata_index(self):
        """
        Stores the metadata index to a file.

        Parameters
        ----------
        path : str
            The path to the directory where the indexes are stored.
        """
        path =  self.path + Indexes.DOCUMENTS.value + '_' + Index_types.METADATA.value + '_index.json'
        with open(path, 'w') as file:
            json.dump(self.metadata_index, file, indent=4)

    
if __name__ == "__main__":
    meta_index = Metadata_index(os.getcwd() + "/Logic/Data/")
    meta_index.store_metadata_index()