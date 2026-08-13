import os
import numpy as np
import librosa
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import pickle

def extract_features(file_path):
    audio, sr = librosa.load(file_path, sr=16000)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

print("Loading your voice samples...")

X = []
y = []

# Load wake word samples
wake_word_folder = "wake_words"
for file in os.listdir(wake_word_folder):
    if file.endswith(".wav"):
        features = extract_features(os.path.join(wake_word_folder, file))
        X.append(features)
        y.append(1)

# Generate negative samples (silence/random)
print("Generating background samples...")
for i in range(20):
    noise = np.random.normal(0, 0.01, 16000 * 3).astype(np.float32)
    mfcc = librosa.feature.mfcc(y=noise, sr=16000, n_mfcc=13)
    X.append(np.mean(mfcc.T, axis=0))
    y.append(0)

X = np.array(X)
y = np.array(y)

# Train
print("Training your personal wake word detector...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = SVC(kernel='rbf', probability=True)
model.fit(X_scaled, y)

# Save
with open("wake_word_model.pkl", "wb") as f:
    pickle.dump((model, scaler), f)

print("Done! wake_word_model.pkl saved successfully!")