# -*- coding: utf-8 -*-
"""
Iopf model class

Created on Mon Jul 30 17:25:22 2018

@author: kkalla
"""


from keras.layers import Input, GRU, Dense, Dropout, BatchNormalization,\
Activation
from keras.models import Model,load_model
from keras.optimizers import SGD,Adam
from keras.callbacks import TensorBoard
from keras.utils import plot_model

class IopfModel():
    def __init__(self,
                 model_path=None,
                 is_pretrained = False,
                 timesteps=1,
                 out_len=1,
                 data_dim=1,
                 learning_rate = 0.001,
                 decay = 0,
                 loss = 'mean_squared_error',
                 optimizer = 'adam',
                 momentum=0
                 ):

        self.model_path = model_path
        self.is_pretrained = is_pretrained
        self.timesteps=timesteps
        self.out_len=out_len
        self.data_dim=data_dim
        self.learning_rate = learning_rate
        self.decay = decay
        self.loss = loss
        self.optimizer = optimizer


    def build(self):
        main_input = Input(shape=(self.timesteps,self.data_dim),
                           dtype='float32',name='main_input')
        X = BatchNormalization()(main_input)
        X = Activation('relu')(X)
        X = Dropout(0.8)(X)
        X = GRU(128, return_sequences = True,
                input_shape=(self.timesteps,self.data_dim),
                dropout=0.8)(X)
        X = BatchNormalization()(X)
        X = GRU(128,dropout=0.8)(X)
        X = BatchNormalization()(X)
        X = Dropout(0.8)(X)
        X = Dense(16, activation = 'relu')(X)
        X = Dropout(0.5)(X)
        main_output = Dense(self.out_len,name='main_output',
                            activation='sigmoid')(X)

        self.model = Model(inputs=main_input,outputs=main_output)

    def train(self,input_X,output_Y,epochs=200,batch_size=32,
              save_model=True,log_dir='log',
              validation_split=0.1):
        # If there is a pre-trained model, load it.
        if self.is_pretrained:
            model = load_model(self.model_path)
        else:
            self.build()
            model = self.model

        if self.optimizer == 'adam':
            optimizer = Adam(lr=self.learning_rate,decay=self.decay)
        else:
            optimizer = SGD(lr=self.learning_rate,momentum=self.momentum,
                            decay=self.decay)

        loss = self.loss
        print("Compiling model...")
        model.compile(optimizer=optimizer,loss=loss)

        print("Model summary")
        print("="*50)
        print(model.summary())

        callbacks=[TensorBoard(log_dir=log_dir)]

        history = model.fit(input_X,output_Y,
                            epochs=epochs,
                            batch_size=batch_size,
                            callbacks = callbacks,
                            validation_split=validation_split)

        self.history = history

        print("Saving model...")
        if save_model:
            model.save(self.model_path)
            plot_model(model,to_file='IopfModel.png')



    def test(self,test_X,test_Y,sc):
        # If there is a pre-trained model, load it.
        if self.is_pretrained:
            model = load_model(self.model_path)

        pred_Y = model.predict(test_X)
        pred_Y = sc.inverse_transform(pred_Y.reshape((-1,1)))

        return pred_Y