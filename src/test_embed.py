from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

texts = [
    "What is dengue?",
    "Dengue is a mosquito-borne viral disease.",
    "The capital of Nepal is Kathmandu.",
]
vecs = model.encode(texts, normalize_embeddings=True)

print("Shape:", vecs.shape)
print("Question vs dengue sentence:  ", float(vecs[0] @ vecs[1]))
print("Question vs Kathmandu sentence:", float(vecs[0] @ vecs[2]))