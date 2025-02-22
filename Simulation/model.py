import pandas as pd 
import numpy as np 
from keras.layers import Lambda
from keras.layers import MaxPooling2D,Dense
from keras.layers import Conv2D, Flatten,Dropout
from keras.models import Sequential
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split 
from utils import INPUT_SHAPE, batch_generator
import argparse
import os
np.random.seed(0)

def build_model(args):
    model = Sequential()
    model.add(Lambda(lambda x: x/127.5-1.0, input_shape=INPUT_SHAPE))
    model.add(Conv2D(16, 8, 8, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(32, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(64, 5, 5, activation='elu', subsample=(4, 2)))
    #model.add(Conv2D(52, 3, 3, activation='elu'))
    #model.add(Conv2D(30, 5, 3, activation='elu'))
    #model.add(Conv2D(24, 3, 3, activation='elu'))
    model.add(Flatten())
    model.add(Dropout(.2))
    model.add(Dense(512, activation='elu'))
    #model.add(Dense(70, activation='elu'))
    model.add(Dense(50, activation='elu'))
    model.add(Dense(1))
    model.summary()
    return model

def train_model(model, args, X_train, X_valid, y_train, y_valid):
    checkpoint = ModelCheckpoint('model-{epoch:03d}.h5',
                                 monitor='val_loss',
                                 verbose=0,
                                 save_best_only=args.save_best_only,
                                 mode='auto')
    model.compile(loss='mean_squared_error', optimizer=Adam(lr=args.learning_rate),metrics=['accuracy'])
    model.fit_generator(batch_generator(args.data_dir, X_train, y_train, args.batch_size, True),
                        args.samples_per_epoch,args.nb_epoch,max_q_size=1,
                        validation_data=batch_generator(args.data_dir, X_valid, y_valid, args.batch_size, False),
                        nb_val_samples=len(X_valid),callbacks=[checkpoint],verbose=1)
    #predict=model.predict_classes(X_test)
    #from sklearn.metrics import accuracy_score
    #score=accuracy_score(y_test,predict)
    #score



def load_data(args):
    data_df = pd.read_csv(os.path.join(os.getcwd(), args.data_dir, 'driving_log.csv'), names=['center', 'left', 'right', 'steering', 'throttle', 'reverse', 'speed'])

    X = data_df[['center', 'left', 'right']].values
    y = data_df['steering'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_size, random_state=0)
    return X_train, X_test, y_train, y_test


def s2b(s):
    s = s.lower()
    return s == 'true' or s == 'yes' or s == 'y' or s == '1'


def main():

    parser = argparse.ArgumentParser(description='Behavioral Cloning Training Program')
    parser.add_argument('-d', help='data directory',        dest='data_dir',          type=str,   default='data')
    parser.add_argument('-t', help='test size fraction',    dest='test_size',         type=float, default=0.2)
    parser.add_argument('-k', help='drop out probability',  dest='keep_prob',         type=float, default=0.5)
    parser.add_argument('-n', help='number of epochs',      dest='nb_epoch',          type=int,   default=10)
    parser.add_argument('-s', help='samples per epoch',     dest='samples_per_epoch', type=int,   default=20000)
    parser.add_argument('-b', help='batch size',            dest='batch_size',        type=int,   default=40)
    parser.add_argument('-o', help='save best models only', dest='save_best_only',    type=s2b,   default='true')
    parser.add_argument('-l', help='learning rate',         dest='learning_rate',     type=float, default=1.0e-4)
    args = parser.parse_args()

    print('-' * 30)
    print('Parameters')
    print('-' * 30)
    for key, value in vars(args).items():
        print('{:<20} := {}'.format(key, value))
    print('-' * 30)

    data = load_data(args)
    model = build_model(args)
    train_model(model, args, *data)

if __name__ == '__main__':
    main()

