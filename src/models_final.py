### Librerias ###

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, f1_score

########################
### Redes Neuronales ###
########################

def crear_modelo_nn(input_dim=132, layer1=128, layer2=64, dropout=0.3, lr=0.001):
    model = Sequential([
        Input(shape=(input_dim,)),
        
        Dense(layer1, activation='relu'),
        BatchNormalization(),
        Dropout(dropout),
        
        Dense(layer2, activation='relu'),
        BatchNormalization(),
        Dropout(dropout),
        
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=lr),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )
    return model

"""
juego_hyperparametros_nn = [
    {"layer1": 128, "layer2": 64,  "dropout": 0.3, "lr": 0.001, "batch_size": 64},
    {"layer1": 256, "layer2": 128, "dropout": 0.4, "lr": 0.001, "batch_size": 128},
    {"layer1": 64,  "layer2": 32,  "dropout": 0.2, "lr": 0.0005,"batch_size": 64},
]
"""

def probar_hyperparametros_nn(X_train, X_test, y_train, y_test, juego_hyperparametros):

    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    for i, params in enumerate(juego_hyperparametros):
        print(f"\n--- Test NN {i+1}/{len(juego_hyperparametros)} : {params} ---")
        
        model = crear_modelo_nn(
            input_dim=X_train.shape[1],
            layer1=params["layer1"],
            layer2=params["layer2"],
            dropout=params["dropout"],
            lr=params["lr"]
        )

        history = model.fit(
            X_train, y_train,
            validation_split=0.2,
            epochs=50,
            batch_size=params["batch_size"],
            callbacks=[early_stop],
            verbose=0
        )
        
        y_pred_proba = model.predict(X_test).ravel()
        auc = roc_auc_score(y_test, y_pred_proba)
        print(juego_hyperparametros[i])
        print(f"ROC-AUC sur Test : {auc:.4f}")
