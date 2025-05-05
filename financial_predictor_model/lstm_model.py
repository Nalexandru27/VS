import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
from data_preprocessing import prepare_data_for_lstm

class StockPriceLSTM:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.model = None
        self.scalar = None
        self.history = None
        self.original_df = None

    def build_model(self, input_shape):
        """
        Construiește arhitectura modelului LSTM
        """

        model = Sequential()

        # Primul strat LSTM cu 50 unitati
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))

        # Al doilea strat LSTM
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))

        # Strat Dense pentru output
        model.add(Dense(units=1))

        model.compile(optimizer='adam', loss='mean_squared_error')

        self.model = model
        return model
    
    def train(self, ticker, start_date, end_date, epochs=50, batch_size=32):
        """
        Antrenează modelul LSTM pe datele furnizate
        """

        # Pregatim datele
        X_train, X_test, y_train, y_test, scaler, df = prepare_data_for_lstm(ticker, start_date, end_date, self.sequence_length)

        # Salvam scaler-ul si dataframe-ul original pentru predictii ulterioare
        self.scaler = scaler
        self.original_df = df

        # Construim modelul daca nu exista deja
        if self.model is None:
            self.build_model((X_train.shape[1], X_train.shape[2]))

       # Implementăm Early Stopping pentru a preveni overfitting-ul
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        # Antrenam modelul
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stop],
            verbose=1
        )

        return self.history
    
    def evaluate(self, X_test, y_test):
        """
        Evaluează performanța modelului pe setul de test
        """
        loss = self.model.evaluate(X_test, y_test, verbose=0)
        print(f'Test Loss: {loss}')
        return loss
    
    def predict(self, X_test):
        """
        Face predicții utilizând modelul antrenat
        """
        predictions = self.model.predict(X_test)
        return predictions
    
    def plot_training_history(self):
        """
        Vizualizează evoluția pierderii în timpul antrenamentului
        """
        plt.figure(figsize=(12,6))
        plt.plot(self.history.history['loss'], label='Train Loss')
        plt.plot(self.history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss During Training')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_predictions(self, ticker, start_date, end_date):
        """
        Vizualizează predicțiile modelului versus valorile reale
        """

        # Pregătim din nou datele pentru predicții
        _, X_test, _, y_test, _, _ = prepare_data_for_lstm(
            ticker, start_date, end_date, self.sequence_length
        )

        # Facem predictiile
        predicted_prices = self.predict(X_test)

        # Inversam normalizarea pentru a obtine preturi reale
        close_price_index = self.original_df.columns.get_loc('Close')

        # Creăm un dataframe pentru vizualizare
        test_dates = self.original_df.index[-len(y_test):]

        plt.figure(figsize=(16,8))
        plt.plot(test_dates, y_test, label='Preturi reale', color='blue')
        plt.plot(test_dates, predicted_prices, label='Predictii', color='red')
        plt.title(f'Predictii LSTM pentru {ticker}')
        plt.xlabel('Data')
        plt.ylabel('Pret (normalizat)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def save_model(self, filepath):
        """
        Salvează modelul antrenat pentru utilizări ulterioare
        """
        self.model.save(filepath)
        print(f"Model salvat la: {filepath}")

    @classmethod
    def load_model(cls, filepath, sequence_length=60):
        """
        Încarcă un model salvat anterior
        """
        instance = cls(sequence_length)
        instance.model = tf.keras.models.load_model(filepath)
        print(f'Model incarcat din: {filepath}')
        return instance
