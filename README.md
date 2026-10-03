# HexPerts Smart Agriculture Platform

An AI platform that helps farmers make data-driven decisions. It combines three models:

| Module | Model | Output |
|---|---|---|
| Plant disease diagnosis | MobileNetV3-Large (PyTorch, `timm`), 38 PlantVillage classes | Crop + disease (or healthy) with confidence |
| Smart irrigation | Random Forest (scikit-learn) | Whether irrigation is needed, with confidence |
| Agricultural advisor | RAG: ChromaDB + `all-MiniLM-L6-v2` + Gemini | Recommendation grounded in a knowledge base |

## How the pipeline works

```
leaf image ──► CNN ──► crop + disease ─┐
field readings ──► Random Forest ──────┼──► consistency checks ──► RAG (Gemini) ──► recommendation
selected crop ─────────────────────────┘
```

- The LLM never changes the CNN or irrigation results; it only writes a recommendation from retrieved knowledge.
- If the photo does not match the selected crop, no disease-specific advice is generated.
- If the knowledge base has no matching information, the system says so instead of guessing.

## Project structure

```
app.py                  Streamlit app
api/main.py             FastAPI backend (POST /predict)
models/
  cnn_model.py          plant disease model
  irrigation_model.py   irrigation model (validates inputs)
  rag_chain.py          retrieval + Gemini recommendation
  safety.py             hazardous-substance filter
views/                  Streamlit tabs
styles/custom_css.py    UI styling
artifacts/              trained models and preprocessing files
build_rag.py            builds the ChromaDB knowledge base
retrain_irrigation_model.py   re-saves the irrigation model with the installed scikit-learn
postman/                Postman collection and test images (API tests)
test_*.py               test scripts
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # then put your GEMINI_API_KEY in .env
python build_rag.py               # builds rag_data/chroma (downloads the dataset)
```

## Run

```bash
streamlit run app.py              # web interface
python -m uvicorn api.main:app   # API, docs at http://127.0.0.1:8000/docs (run ONE server only)
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -F "image=@tomato_leaf.jpg" -F "crop_id=Tomato" -F "soil_type=Loam Soil" \
  -F "seedling_stage=Vegetative Growth / Root or Tuber Development" \
  -F "MOI=40" -F "temp=25" -F "humidity=60" \
  -F "user_query=How can I manage this plant disease?"
```

The response contains `plant_analysis`, `irrigation`, `recommendation` and a `warnings` list
(crop/photo mismatch, low confidence).

`recommendation` is one unified text with three sections (Plant health, Irrigation, Recommended
actions) followed by a safety notice. When the photo does not match the selected crop, or the plant is
healthy and no question was asked, the language model is not called: a fixed message and a factual
irrigation sentence are returned instead. Every response carries the header `X-Process-Time-ms`
(server processing time).

## Testing

- Unit-style scripts: `python test_safety.py`, `python test_irrigation_integration.py` (and the other `test_*.py`).
- API tests with Postman (`postman/`): import `HexPerts_API.postman_collection.json`, set Postman's
  Working directory to the `postman` folder, start the API and run the folders in order.
  It covers the field/plant scenarios, crop-photo consistency, input validation, safety and grounding.
  Run folder `05 - Latency benchmark` with 10 iterations to get average, p95 and the server-side time.
  See `postman/README.md`.

## Retraining the irrigation model

The artifacts in `artifacts/` must be saved with the scikit-learn version that runs the app, otherwise
scikit-learn prints an `InconsistentVersionWarning`. To retrain and re-save them with the installed version,
give the script the project's preprocessed dataset (zip or folder):

```bash
python retrain_irrigation_model.py "C:\path\to\Smart_Agriculture_Preprocessed.zip"
```

The script checks that the data matches the saved scaler, retrains with the documented configuration
(GridSearchCV over n_estimators [50, 100] and max_depth [5, 10], cv=3), compares the new model with the
current one on train / validation / test, and only replaces it if it is not worse. The encoder and scaler
are re-saved without refitting, because the dataset was preprocessed with them. The previous files are
kept in `artifacts/backup_before_retrain/`. Restart the API and the app afterwards.

## Safety

Sentences that recommend highly toxic or banned substances (for example mercuric chloride) are
removed when the database is built; the safe advice around them is kept, and documents left with
too little text are dropped. Retrieval filters the same terms again as a second layer. Every
recommendation ends with a notice to consult an agronomist and follow local regulations.
The substance list in `models/safety.py` is a starting point and should be reviewed by an expert.

## Limitations

- The disease model was trained on PlantVillage-style images (single leaf, plain background).
  Field photos with cluttered backgrounds can be misclassified.
- The irrigation model predicts whether irrigation is needed; it does not estimate a water volume.
  It supports Carrot, Chilli, Potato, Tomato and Wheat.
- The disease and irrigation models share only some crops (Tomato, Potato, Pepper/Chilli).
- The Streamlit app calls the models directly; the FastAPI backend is meant for other clients
  (mobile app, tests, integrations).
- The knowledge base covers a limited set of crops and diseases; for others the system answers
  that it does not have enough information.
