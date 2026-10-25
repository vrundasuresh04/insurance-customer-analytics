# Insurance Customer Analytics Dashboard

An interactive Streamlit dashboard built with the CoIL 2000 insurance benchmark training data.

## Run the dashboard

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install the packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```bash
   python -m streamlit run app.py
   ```

The app reads `ticdata2000_with_headers.csv` from this folder automatically. You can also upload a CSV from the dashboard sidebar.

## What it shows

- Six interactive filters
- Four KPI cards
- Six charts showing caravan policy patterns by coded customer/area profiles and existing product portfolio
- Filter-aware key insights

The supplied training data contains 5,822 customers and 348 caravan policyholders (about 5.98%). Profile code ranges determine the customer cohort used by the KPI cards, purchase-rate charts, and key insights. The Caravan policy status dropdown filters the two customer-count charts so the purchase-rate comparisons continue to include both policy outcomes.

## Data limitations

The age, income, relationship, and vehicle profile fields are coded area-level categories. They do not identify an individual customer's exact age, income, relationship status, or vehicle ownership. The dataset does not contain a policy start date or tenure field. For that reason, the dashboard shows existing product portfolio as a substitute analysis and does not label it as tenure.

This dataset is provided for non-commercial research and educational use. Check the original dataset terms before redistributing it. If the repository is public, the CSV will be publicly downloadable too.

## Project files

- `app.py` — Streamlit dashboard source code
- `requirements.txt` — Python dependencies
- `ticdata2000_with_headers.csv` — training data with descriptive column names
- `README.md` — project notes and setup instructions
