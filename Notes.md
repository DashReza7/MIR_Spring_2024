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
 - **Important**: run any file from the directory `MIR_SPRING_2024`
 - What should be the `index document` function in `index.py`
 - Check the `jaccard_score` in `LSH` and `spell_correction`. It might be broken when one set or both of them are empty
 - `CrawlerResults`: `/MIR_SPRING_2024/Logic/tests/CrawlerResults`
 - Other Data: `/MIR_SPRING_2024/Data`