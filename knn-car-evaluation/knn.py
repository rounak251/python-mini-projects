"""
============================================================
K-Nearest Neighbor (KNN) Classifier — Car Evaluation Dataset
============================================================
Aim   : Implement KNN on the UCI Car Evaluation dataset and
        compute classifier accuracy with test samples.
Author: ML Lab
============================================================
"""

# ── 1. Import Libraries ──────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')           # non-interactive backend for file output
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection   import train_test_split, cross_val_score
from sklearn.preprocessing     import OneHotEncoder, LabelEncoder
from sklearn.neighbors         import KNeighborsClassifier
from sklearn.metrics           import (accuracy_score, confusion_matrix,
                                       classification_report, ConfusionMatrixDisplay)
from sklearn.pipeline          import Pipeline
from sklearn.compose           import ColumnTransformer

# ── 2. Load Dataset ──────────────────────────────────────────────────────────
COLUMNS = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']

df = pd.read_csv('car.csv', header=None, names=COLUMNS)

print("=" * 60)
print("        CAR EVALUATION DATASET — KNN CLASSIFIER")
print("=" * 60)
print(f"\n[INFO] Dataset shape : {df.shape}")
print(f"[INFO] Features      : {COLUMNS[:-1]}")
print(f"[INFO] Class labels  : {df['class'].unique().tolist()}")
print("\n[SAMPLE] First 5 rows:")
print(df.head().to_string(index=False))

# ── 3. Exploratory Data Analysis ─────────────────────────────────────────────
print("\n[INFO] Class distribution:")
print(df['class'].value_counts().to_string())

# ── 4. Separate Features and Target ─────────────────────────────────────────
X = df.drop(columns=['class'])          # Feature matrix
y = df['class']                         # Target vector

# ── 5. Train-Test Split (BEFORE any encoding to prevent data leakage) ────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y          # preserve class distribution in both splits
)

print(f"\n[SPLIT] Training samples : {len(X_train)}")
print(f"[SPLIT] Testing  samples : {len(X_test)}")

# ── 6. Preprocessing — One-Hot Encoding (fitted only on training data) ───────
categorical_features = COLUMNS[:-1]

preprocessor = ColumnTransformer(transformers=[
    ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
     categorical_features)
])

# ── 7. Build KNN Pipeline ────────────────────────────────────────────────────
K = 7       # chosen value of K (odd to avoid ties)

knn_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('knn',          KNeighborsClassifier(n_neighbors=K, metric='euclidean'))
])

# ── 8. Train the Model ───────────────────────────────────────────────────────
knn_pipeline.fit(X_train, y_train)
print(f"\n[TRAIN] KNN model trained with K = {K}")

# ── 9. Predict on Test Set ───────────────────────────────────────────────────
y_pred = knn_pipeline.predict(X_test)

# ── 10. Accuracy ─────────────────────────────────────────────────────────────
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"\n[RESULT] Test Accuracy : {accuracy:.2f}%")

# ── 11. Cross-Validation Accuracy ────────────────────────────────────────────
cv_scores = cross_val_score(knn_pipeline, X, y, cv=5, scoring='accuracy')
print(f"[RESULT] 5-Fold CV Accuracy : {cv_scores.mean()*100:.2f}% "
      f"(± {cv_scores.std()*100:.2f}%)")

# ── 12. Confusion Matrix ─────────────────────────────────────────────────────
labels = ['unacc', 'acc', 'good', 'vgood']
cm = confusion_matrix(y_test, y_pred, labels=labels)

print("\n[RESULT] Confusion Matrix:")
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
cm_df.index.name   = 'Actual'
cm_df.columns.name = 'Predicted'
print(cm_df.to_string())

# ── 13. Classification Report ─────────────────────────────────────────────────
print("\n[RESULT] Classification Report:")
print(classification_report(y_test, y_pred, target_names=labels, zero_division=0))

# ── 14. Sample Predictions (10 test cases) ───────────────────────────────────
print("[RESULT] Sample Test Predictions (first 10):")
print("-" * 70)
sample = X_test.head(10).copy()
sample['Actual']    = y_test.head(10).values
sample['Predicted'] = y_pred[:10]
sample['Match']     = sample['Actual'] == sample['Predicted']
print(sample.to_string(index=False))

# ── 15. Predict on Custom / Unseen Samples ────────────────────────────────────
print("\n[DEMO] Predicting on custom unseen samples:")
print("-" * 70)

custom_samples = pd.DataFrame([
    # buying, maint, doors, persons, lug_boot, safety
    ['low',   'low',   '4',     'more', 'big',   'high'],   # expected: vgood/good
    ['vhigh', 'vhigh', '2',     '2',    'small', 'low'],    # expected: unacc
    ['med',   'low',   '4',     '4',    'med',   'high'],   # expected: good/acc
    ['high',  'high',  '3',     '2',    'small', 'med'],    # expected: unacc/acc
    ['low',   'med',   '5more', 'more', 'big',   'high'],   # expected: vgood
], columns=categorical_features)

custom_preds = knn_pipeline.predict(custom_samples)

for i, (_, row) in enumerate(custom_samples.iterrows()):
    features = dict(row)
    print(f"  Sample {i+1}: {features}")
    print(f"           → Predicted class : [{custom_preds[i].upper()}]\n")

# ── 16. Effect of K on Accuracy (for analysis) ───────────────────────────────
k_values    = range(1, 21)
k_accuracies = []

for k in k_values:
    pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('knn',          KNeighborsClassifier(n_neighbors=k, metric='euclidean'))
    ])
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    k_accuracies.append(accuracy_score(y_test, pred) * 100)

best_k   = k_values[np.argmax(k_accuracies)]
best_acc = max(k_accuracies)
print(f"[ANALYSIS] Best K = {best_k} with accuracy = {best_acc:.2f}%")

# ── 17. Visualisations ───────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("KNN Classifier — Car Evaluation Dataset", fontsize=14, fontweight='bold')

# (a) Confusion Matrix heatmap
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=labels, yticklabels=labels, ax=axes[0])
axes[0].set_title(f"Confusion Matrix  (K={K})")
axes[0].set_xlabel("Predicted")
axes[0].set_ylabel("Actual")

# (b) K vs Accuracy curve
axes[1].plot(list(k_values), k_accuracies, marker='o', color='steelblue', linewidth=2)
axes[1].axvline(best_k, linestyle='--', color='red', label=f'Best K={best_k}')
axes[1].set_title("Accuracy vs K Value")
axes[1].set_xlabel("K")
axes[1].set_ylabel("Accuracy (%)")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# (c) Class distribution bar chart
class_counts = df['class'].value_counts().reindex(labels)
colors = ['#d9534f','#5bc0de','#5cb85c','#f0ad4e']
axes[2].bar(class_counts.index, class_counts.values, color=colors)
axes[2].set_title("Class Distribution in Dataset")
axes[2].set_xlabel("Class")
axes[2].set_ylabel("Count")
for i, v in enumerate(class_counts.values):
    axes[2].text(i, v + 10, str(v), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('knn_results.png', dpi=150, bbox_inches='tight')
print("\n[INFO] Visualisation saved → knn_results.png")
print("=" * 60)
print("                    PROGRAM COMPLETE")
print("=" * 60)