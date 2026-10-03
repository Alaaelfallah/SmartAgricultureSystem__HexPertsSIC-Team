# Postman tests for the HexPerts API (WBS 6.4)

Tests the `POST /predict` pipeline (CNN + irrigation model + RAG) and the validation rules of the API.

## Files
- `HexPerts_API.postman_collection.json`: 21 requests in 6 folders, each with automatic tests
- `test_files/`: images used by the requests
  - `tomato_bacterial_spot.jpg`: PlantVillage leaf, classified as `Tomato___Bacterial_spot`
  - `tomato_stock_photo.jpg`: photo with a white background (outside the training distribution)
  - `not_an_image.txt`: must be rejected by the API
  - **`tomato_healthy.jpg` is NOT included**: add a healthy tomato leaf from PlantVillage (`Tomato___healthy`).
    It is needed by requests 1.2 and 1.4 only.

## Run
1. Start ONE API server from the project root: `python -m uvicorn api.main:app`
2. Postman: Import the collection JSON.
3. Make the file paths work: set Postman's *Working directory* to this `postman` folder
   (Settings > General), or select the image by hand in each request (Body > form-data > image).
4. Run the folders in order (Run folder / Collection Runner). Folder 05 needs *Iterations = 10*.

## What is checked
- Every successful `/predict` response (collection-level tests): JSON structure, irrigation status matches
  the prediction, no toxic or banned chemical in the recommendation, response time below `max_latency_ms`.
- Scenario tests: dry field / wet field with infected / healthy plant, crop that does not match the photo,
  crop not covered by the disease model, out-of-distribution photo.
- Validation tests: invalid growth stage, crop or soil, out-of-range numbers, missing image, non-image file.
- Grounding tests: chemical-treatment question, off-topic question (LLM-dependent).
- Latency benchmark: average / min / p95 / max of `/predict` over the iterations.

## Variables (collection > Variables)
| name | default | meaning |
|---|---|---|
| `base_url` | `http://127.0.0.1:8000` | where the API runs |
| `max_latency_ms` | `20000` | maximum time allowed for one `/predict` call |
| `avg_latency_ms` | `10000` | maximum average time in the latency summary |

The two latency limits are starting values: adjust them after the first measurements.

## Command line (optional, needs Node.js)
```
npm install -g newman
newman run HexPerts_API.postman_collection.json --working-dir .
```
