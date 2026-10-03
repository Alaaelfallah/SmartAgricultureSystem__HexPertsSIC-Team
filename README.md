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
scripts/
  build_rag.py           builds the ChromaDB knowledge base
  inspect_ckpt.py        inspects the CNN checkpoint
tests/                  project test scripts
```

## Setup

Run these commands in PowerShell from the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Create .env in the project root and add GEMINI_API_KEY=your_api_key_here
.\.venv\Scripts\python.exe -m scripts.build_rag
```

## Run

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Run the safety checks from the project root with:

```powershell
.\.venv\Scripts\python.exe -m tests.test_safety
```

The API documentation is available at http://127.0.0.1:8000/docs.

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
- The knowledge base covers a limited set of crops and diseases; for others the system answers
  that it does not have enough information.
