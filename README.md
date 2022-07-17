# Baustein_Reader
This tool is able to read requirements from a [BSI Baustein PDF](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/IT-Grundschutz-Kompendium/IT-Grundschutz-Bausteine/Bausteine_Download_Edition_node.html) and compare their similarity to requirements from another one. This enables an automatic detection of changes between different iterations. This is crucial since not all changes are tracked by the BSI in a separate document which means that they must be manually extracted from the respective Bausteine. To detect the changes between requirements, the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) is used which shows the number of string operations needed to transform one string into the other.

# Usage

## Python Dependencies

Before we can run the tool, the following Python dependencies are required:

 - [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/) >=0.18.0 # implements string comparison functionality
 - [python-Levenshtein](https://pypi.org/project/python-Levenshtein/) >= 0.12.2 # implements the Levenshtein algorithm
 - [pypdfium2](https://pypi.org/project/pypdfium2/) >=2.5.0 # can read text from a PDF

The dependencies can be installed the following way (it is generally recommended to install these dependencies in a separate virtual environment):

```
pip install pypdfium2 fuzzywuzzy[speedup]
```

Using the `[speedup]` parameter automatically installs `python-Levenshtein`.

**Note:** `pypdfium2` requires to have both `git` and `gcc` installed and available in `PATH`

## Developement Dependencies

The only development dependency is [flake8](https://pypi.org/project/flake8/).

## Run the Tool

To run the tool, simply execute the following python command:

```
python caller.py --file-old [path/to/old_baustein] --file-new [path/to/new_baustein]
```

the tool will automatically create a text file in the project directory containing the results.

### Example

```
python caller.py --file-old SYS_1_1_Allgemeiner_Server_Edition_2021.pdf --file-new SYS_1_1_Allgemeiner_Server_Edition_2022.pdf
```

The output of the previous example and more can be found in the `example_outputs` folder.