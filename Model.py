# Author: Franca Speth
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense, Input, Dropout
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from keras import optimizers
import time
from keras.models import load_model
import matplotlib.pyplot as plt


class Model():
    '''
    Class for Autoencoder Model Training
    '''
    def __init__(self, epochs, batch, lr, num_layers, numfeatures, timestep):
        self.epochs = epochs
        self.batch = batch
        self.lr = lr
        self.num_layers = num_layers
        self.numfeatures = numfeatures
        self.timestep = timestep
        self.name = None
        self.hidden_neurons = [128, 64, 64, 128]

    def deepautoencoder(self,train, valid):
        model = Sequential()
        #Encoder
        model.add(Dense(self.num_layers, activation='relu',
                                  input_shape=(self.numfeatures,)))
        #model.add(Dropout(0.2))
        model.add(Dense(self.num_layers/2, activation='relu'))
        #Decoder
        model.add(Dense(self.num_layers / 2, activation='relu'))
        #model.add(Dropout(0.2))
        #for i, hidden_neurons in enumerate(self.hidden_neurons, 1):
         #   model.add(Dense(
          #      hidden_neurons,
          #      activation='relu'))
           # model.add(Dropout(0.2))
        model.add(Dense(self.numfeatures, activation='relu'))
        adam = optimizers.Adam(self.lr)
        model.compile(loss='mse', optimizer=adam)
        history = model.fit(train, train,
                                       epochs=self.epochs,
                                       batch_size=self.batch,
                                       validation_data=(valid, valid),
                                       verbose=2).history
        self.plot_improvement_over_epochs(Autoencoder=history)
        return model, history

    def lstmautoencoder(self,train,valid):
        lstm_autoencoder = Sequential()
        # Encoder
        lstm_autoencoder.add(LSTM(self.num_layers, activation='relu',
                                  input_shape=(self.timestep, self.numfeatures), return_sequences=True))
        lstm_autoencoder.add(LSTM(int(self.num_layers/2), activation='relu', return_sequences=False))
        lstm_autoencoder.add(RepeatVector(self.timestep))
        # Decoder
        lstm_autoencoder.add(LSTM(int(self.num_layers/2), activation='relu', return_sequences=True))
        lstm_autoencoder.add(LSTM(self.num_layers, activation='relu', return_sequences=True))
        lstm_autoencoder.add(TimeDistributed(Dense(self.numfeatures)))

        print(lstm_autoencoder.summary())
        adam = optimizers.Adam(self.lr)
        lstm_autoencoder.compile(loss='mse', optimizer=adam)
        lstm_autoencoder_history = lstm_autoencoder.fit(train, train,
                                                        epochs=self.epochs,
                                                        batch_size=self.batch,
                                                        validation_data=(valid, valid),
                                                        verbose=2).history
        self.plot_improvement_over_epochs(Autoencoder=lstm_autoencoder_history)
        return lstm_autoencoder, lstm_autoencoder_history

    def plot_improvement_over_epochs(self, Autoencoder):
        plt.plot(Autoencoder['loss'], linewidth=2, label='Train')
        plt.plot(Autoencoder['val_loss'], linewidth=2, label='Valid')
        plt.legend(loc='upper right')
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.show()

    def save_model(self,lstm_autoencoder, info = ''):
        l = time.asctime().split()
        timestamp = l[2] + l[1] + l[4] + l[3].replace(':', '')
        name = 'Autoencoder'+info+timestamp+'.h5'
        lstm_autoencoder.save(name) # saves it in the current environment
        self.name = name
   # def fit_model(self, train, valid):
    #    return lstm_autoencoder_history
