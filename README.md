# DataLens — CSV EDA dashboard

A polished, interactive exploratory data analysis app built with Python, Streamlit, pandas, and Plotly. Upload a CSV to get a dataset overview, data quality checks, column distributions, correlations, scatter plots, and a searchable preview.

## Run in VS Code

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:

   **Windows PowerShell**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install the packages and start the app:

   ```bash
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

Streamlit opens the dashboard in your browser. Use **Choose a CSV file** in the left sidebar to load your data. The included `synthetic_student_support.csv` can be used as a sample.

## What’s included

- Dataset size, column types, missingness, duplicate-row counts, and file size
- Numeric summaries and distributions, with histograms and box plots
- Categorical value counts and completeness by column
- Numeric correlation heatmap and interactive scatter plot with optional color groups
- Searchable data preview and CSV download

The app reads the uploaded file for the current Streamlit session and does not save it to disk.
