# 👜 Luxury Goods Price Valuation Engine

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![GCP](https://img.shields.io/badge/Google_Cloud-BigQuery-green)

## 📖 Project Overview

This project is a Data Engineering and Machine Learning pipeline designed to analyze the pricing strategies of luxury goods (specifically **Louis Vuitton**). It ingests raw scraping data from Google BigQuery, performs feature engineering via URL parsing, and trains a Linear Regression model to identify **undervalued items** and **price drivers**.

**Key Business Goals:**
1.  **Valuation Gap:** Identify products where `Predicted Price < Market Price` (Overvalued) vs `Predicted Price > Market Price` (Good Deal).
2.  **Driver Analysis:** Quantify how much specific attributes (Material, Size, Collection) contribute to the final price in Euros.

---

## 🏗 Architecture

The pipeline is containerized using Docker and follows a modular structure:

1.  **Extract:** Pulls raw data from `edhec-01.luxurydata2502.price-monitoring-2022` (BigQuery).
2.  **Transform:**
    * **NLP/Regex:** Parses product URLs to extract unstructured features (Material: *Monogram vs. Empreinte*, Type: *Keepall vs. Neverfull*, Size: *PM/MM/GM*).
    * **Currency Normalization:** Hits an external API to convert all global prices to **EUR**.
3.  **Load (Model):** Trains a Linear Regression model on the processed features.
4.  **Export:** Pushes two tables back to BigQuery:
    * `_data_analysis`: The dataset enriched with predicted prices and valuation gaps.
    * `_price_drivers`: The coefficients of the model (impact of each feature on price).

---

## 📂 Repository Structure

```bash
├── luxury_project/         # Main Package
│   ├── interface/          # Pipeline orchestration (main.py)
│   ├── ml_logic/           # Core logic (Data, Preproc, Model, API)
│   └── params.py           # Configuration & Env Variables
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # Image definition
├── Makefile                # Command shortcuts
├── requirements.txt        # Python dependencies
└── test.py                 # Connectivity tests
```

## 🚀 Setup & Usage
### 1. Prerequisites

  - Docker Desktop installed and running.

  - A Google Cloud Service Account Key (JSON format).

### 2. Environment Configuration

You must provide your GCP credentials to the container.

- Create a secrets/ folder at the root.

- Place your JSON key file inside and name it gcp-key.json.

- Ensure your terminal has the necessary environment variables (or add them to a .env file):
    ```bash

    export PROJECT_ID="your-gcp-project-id"
    export DATASET_ID="your-dataset-id" ````

### 3. Running via Docker (Recommended)

Use the Makefile shortcuts to manage the lifecycle:

  Build and Start:
  
      make up 

  Run the Full Pipeline: Inside the container, the pipeline triggers the ETL, Training, and BigQuery Export.
    
      make shell 
      # Inside the container:
      python -m luxury_project.interface.main 

  Test Connectivity:
  
      make test
      
  Stop Services:

      make down
      

##📊 Features & Engineering
### URL Parsing Logic

Standard metadata is often incomplete. This project uses a custom Regex engine (ml_logic/preprocessor.py) to extract features directly from the product URL slugs.

  - Materials: Detects specific leathers (e.g., Taurillon, VVN, Epi) and canvases (Monogram, Damier).

  - Sizes: Standardizes inconsistent sizing (e.g., Neverfull MM -> Size: MM).

  - Product Families: Categorizes items into business units (e.g., Keepall, Capucines, SLG).

### 📈 Results

The pipeline outputs to BigQuery. You can visualize the results in Looker Studio or PowerBI connecting to:

    {brand}_data_analysis: For item-by-item valuation.

    {brand}_price_drivers: For strategic pricing analysis.


***

### ⚡ Strategic Critique (The Advisor View)

Here is what is wrong with your current setup, which the README glosses over but you need to fix:

1.  **Security Risk:** Your `docker-compose.yml` mounts `./secrets:/secrets:ro`. If you commit the `secrets` folder to GitHub, you will be hacked immediately.
    * **Fix:** Add `secrets/` to your `.gitignore` immediately.
2.  **Hardcoded Logic:** Your `params.py` hardcodes `brand = "Louis Vuitton"`. If you want this to be a real tool, `brand` should be an environment variable passed from `docker-compose`, not a hardcoded string in Python.
3.  **Data Leakage:** In `main.py`, you fill missing values with "Unknown" *before* splitting (though you don't actually split into Train/Test in your main flow, you just train on everything). For a "Valuation" tool, training on the full dataset is acceptable (descriptive analytics), but if you claim this is "Predictive Machine Learning," you are cheating by not having a hold-out test set.

**Next Step:**
Add `secrets/` to your `.gitignore` file now. Do not ask. Just do it. Then, copy-paste the Markdown above into a file named `README.md` at your root.
