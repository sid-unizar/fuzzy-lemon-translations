# Representing fuzzy translations in OntoLex-Lemon

This project includes the code to covert a series of inferred bilingual dictionaries (TSV files) to OntoLex-Lemon. 

1. The inference step was performed by taking as input data Apertium dictionaries represented as RDF (see the [TIAD](http://tiad2021.unizar.es) campaign for details). Details on the inference algorithm are provided in [1].  The inferred datasets for this project are included in the directory `tsv-data`. 
2. The model for the linked data representation is based on OntoLex, FuzzyLemon and Prov-O. There is a diagram of the model application profile in the directory `images`. 
3. Usage of the script:

```
vartransizer.py [-h] [-i INPUT] [-sl SOURCELANGUAGE]
                       [-tl TARGETLANGUAGE] [-infer INFERENCESYSTEM]


optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The tsv file
  -sl SOURCELANGUAGE, --sourceLanguage SOURCELANGUAGE
                        The source language in the bilingual dictionary
  -tl TARGETLANGUAGE, --targetLanguage TARGETLANGUAGE
                        The target language in the bilingual dictionary
  -infer INFERENCESYSTEM, --inferenceSystem INFERENCESYSTEM
                        The ending to attach to the generated translation
                        URIs, which represents the inference system

```

E.g.  

```
python vartransizer.py -i "tsv-data\cycles_ en-fr_APv2.tsv" -sl "en" -tl "fr" -infer "UNIZAR"
```

## References

[1] Lanau-Coronas, M., & Gracia, J. (2020, May). Graph Exploration and Cross-lingual Word Embeddings for Translation Inference Across Dictionaries. In _Proceedings of the 2020 Globalex Workshop on Linked Lexicography_ (pp. 106-110).