```{python}
if __name__ == "__main__":
    preprocessed_documents = None
    with open(os.getcwd() + "/Logic/Data/PreprocessedDocuments.json", "r") as file:
        preprocessed_documents = json.load(file)
    my_index = Index(preprocessed_documents)
    my_index.check_add_remove_is_correct()
    print(my_index.check_if_index_loaded_correctly("documents", my_index.index["documents"]))
    print(my_index.check_if_index_loaded_correctly("stars", my_index.index["stars"]))
    print(my_index.check_if_index_loaded_correctly("genres", my_index.index["genres"]))
    print(my_index.check_if_index_loaded_correctly("summaries", my_index.index["summaries"]))
    my_index.check_if_indexing_is_good("stars", "kenneth")

output: 
Add is correct
Remove is correct
True
True
True
True
Brute force time:  0.0
Implemented time:  0.0
Indexing is correct
Indexing is good
```


### Notes:
 - stars are only being lowercased. No other preprocessing
 - What should be the `index document` function in `index.py`