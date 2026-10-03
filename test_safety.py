from models.safety import (
    contains_hazardous_substance,
    find_hazardous_substances,
    remove_hazardous_sentences,
)


MUST_BLOCK = [
    "Treat seeds with mercuric chloride (1:1000).",
    "Apply Monocrotophos twice a season.",
    "Use carbofuran granules at planting.",
    "Dust with DDT.",
]

MUST_ALLOW = [
    "Use disease-free seeds and rotate crops with non-host crops.",
    "Spray copper fungicide every 7 to 10 days.",
    "Toxic cyanide compounds are removed from cassava by boiling.",
    "Tomato tendrils should be trained on a support.",
]

failed = False

for text in MUST_BLOCK:
    if not contains_hazardous_substance(text):
        failed = True
        print("FAIL (should be blocked):", text)

for text in MUST_ALLOW:
    if contains_hazardous_substance(text):
        failed = True
        print("FAIL (should be allowed):", text, find_hazardous_substances(text))

sample = (
    "Use disease-free seed and rotate crops. "
    "Seed treatment with mercuric chloride (1:1000) is recommended. "
    "Spray copper fungicide every 7 days."
)
cleaned = remove_hazardous_sentences(sample)

if contains_hazardous_substance(cleaned) or "disease-free seed" not in cleaned or "copper fungicide" not in cleaned:
    failed = True
    print("FAIL (redaction):", cleaned)

if remove_hazardous_sentences("Dust with DDT.") != "":
    failed = True
    print("FAIL (redaction should return empty text)")

print("SAFETY TESTS:", "FAILED" if failed else "all passed")
