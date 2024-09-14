# A Comprehensive Study on LLM-based Agent Bug Characteristics

This is a Replication Package for the paper titled "A Comprehensive Study on LLM-based Agent Bug Characteristics".

## Data for the table

The raw data and actual data used for the tables are located in the `Tables Data/` directory.

## Labeled Data

The labeled and finalized files are located in the `labeled_github_issues/` directory.

## Generating Visuals and Percentages

To generate visuals and percentages for each Research Question (RQ):

1. Install the required dependencies:
   ```
   pip install -r src/requirements.txt
   ```

2. Navigate to the specific RQ directory (e.g., `RQ1/`, `RQ2/`, etc.).

3. Convert the labeled GitHub issues into JSON files.

4. Execute the corresponding Python file to generate graphs and analysis.

## Mining GitHub Issues

To mine GitHub issues:

1. Install the required dependencies:
   ```
   pip install -r src/requirements.txt
   ```

2. Run the following command:
   ```
   python collect_github_issues.py
   ```

3. To clean labels without comments, use:
   ```
   python preprocess_buggy_files.py -h
   ```
   This will display the help information for the script.
