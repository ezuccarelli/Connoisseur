import numpy as np
np.random.seed(12321)  # for reproducibility
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers.core import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Convolution2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from io import BytesIO
from keras import backend as K
import urllib
import keras
import tensorflow as tf
import os
import pathlib
path_to_data_dir = '../Datasets/'

nb_classes = 10
num_classes = 10
img_rows, img_cols = 42, 28
nb_epoch = 3
batch_size = 64
K.common.set_image_dim_ordering('th')
# input image dimensions


BATCH_SIZE = 32
IMG_HEIGHT = 224
IMG_WIDTH = 224


def main():
    my_data_dir = '/pool001/ezucca/Connoisseur/Artworks'
    data_dir = pathlib.Path(my_data_dir)
    CLASS_NAMES = np.array([item.name for item in data_dir.glob('*')])
    BATCH_SIZE = 32
    STEPS_PER_EPOCH = np.ceil(len([item.name for item in data_dir.glob('*')]) / BATCH_SIZE)
    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
    BATCH_SIZE = 32
    IMG_HEIGHT = 200
    IMG_WIDTH = 200
    train_data_gen = image_generator.flow_from_directory(directory=str(data_dir),
                                                         batch_size=BATCH_SIZE,
                                                         shuffle=True,
                                                         target_size=(IMG_HEIGHT, IMG_WIDTH),
                                                         classes=list(CLASS_NAMES))
    train_data_gen = image_generator.flow_from_directory(directory=str(data_dir),
                                                         batch_size=BATCH_SIZE,
                                                         shuffle=True,
                                                         target_size=(IMG_HEIGHT, IMG_WIDTH),
                                                         classes=list(CLASS_NAMES))
    X, class_label = next(train_data_gen)
    # Then just use tf.split on this

    inputs = Input(shape=(3, None, None))
    step_1 = Convolution2D(filters=8, kernel_size=(2, 2), activation='relu', padding='same')(inputs)
    step_2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(step_1)
    step_3 = Convolution2D(filters=16, kernel_size=(2, 2), activation='relu', padding='same')(step_2)
    step_4 = MaxPooling2D(pool_size=(2, 2), padding='same', strides=(2, 2))(step_3)
    step_5 = Flatten()(step_4)
    step_6 = Dense(10, activation='relu')(step_5)
    step_7 = Dropout(rate=0.5)(step_6)
    output = Dense(10, activation='softmax')(step_7)

    model = Model(inputs=inputs, outputs=output)

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'], loss_weights=0.5)
    #==================== Fetch Data and Fit ===================#
    model.fit_generator(train_data_gen, nb_epoch=nb_epoch, steps_per_epoch=steps_per_epoch, verbose=1)
    # objective_score = model.evaluate(X_test, y_test, batch_size=32)
    # print('Evaluation on test set:', dict(zip(model.metrics_names, objective_score)))
    #
    # #Uncomment the following line if you would like to save your trained model
    # #model.save('./current_model_conv.h5')
    if K.backend()== 'tensorflow':
        K.clear_session()

if __name__ == '__main__':
    main()
