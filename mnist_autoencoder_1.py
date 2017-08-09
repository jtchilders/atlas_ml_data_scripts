
from __future__ import print_function

import os
import numpy as np
import matplotlib.pyplot as plt
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, Input
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import SGD, RMSprop, Adam, Adagrad, Adadelta, Adamax, Nadam
from keras import backend as K
from keras.utils import np_utils
from keras.models import Model
from keras import backend as K
K.set_image_dim_ordering('tf')
np.set_printoptions(precision=4)
#from sklearn.cross_validation import train_test_split  #will remove it

batch_size = 32
num_classes = 4
# epochs = 20
#epochs = 5
img_rows = 20
img_cols = 10
num_channel = 1
num_epoch = 5

# the data, shuffled and split between train and test sets
#(x_train, y_train), (x_test, y_test) = mnist.load_data()

#x_train = x_train.reshape(60000, 784)
#x_test = x_test.reshape(10000, 784)
#x_train = x_train.astype('float32')
#x_test = x_test.astype('float32')
#x_train /= 255
#x_test /= 255
#print('x_train shape:', x_train.shape)
#print('x_test shape:', x_test.shape)


#num_files = 8800*num_classes


Dir1 = '/users/hpcusers/dumpCaloCells/images2'
data_path = Dir1 + 'TrainingData/'


names = ['electronelectron', 'muonmuon', 'tautau']

img_data_list = []
labels = []


# for name in names:
for labelID in [0, 1, 2]:
    name = names[labelID]
    for img_ind in range(num_files / num_classes):
        fileIn = data_path + '/' + name + '/' + name  + str(img_ind) + '.data'
        
        
        input_img = np.load(fileIn)
        if np.isnan(input_img).any():
            print (labelID, img_ind, ' -- ERROR: NaN')
        
        else:
            img_data = np.resize(input_img,(20,10,2))

            img_data_list.append(input_img[:,:,0])
            img_data_list.append(input_img[:,:,1])
            labels.append(labelID)

img_data = np.array(img_data_list)
#img_data = img_data.astype('float32')
#img_data = 255.*(img_data - img_data.min()) / (img_data.max() - img_data.min())
#img_data /= 255
print (img_data.shape)

'''
if num_channel == 1:
    if K.image_dim_ordering() == 'th':
        img_data = np.expand_dims(img_data, axis=1)
        print (img_data.shape)
    else:
        img_data = np.expand_dims(img_data, axis=4)
        print (img_data.shape)

else:
    if K.image_dim_ordering() == 'th':
        img_data = np.rollaxis(img_data, 3, 1)
        print (img_data.shape)
'''
#X= img_data
#y=np_utils.to_categorical(labels, num_classes)
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=4) #will remove it

X_train = img_data
y_train = np_utils.to_categorical(labels, num_classes)


np.random.seed(123)
shuffleOrder = np.arange(X_train.shape[2])
np.random.shuffle(shuffleOrder)
X_train = X_train[shuffleOrder]
y_train = y_train[shuffleOrder]


print(X_train.shape, 'train samples shape')
print(y_train.shape, 'test samples shape')

input_shape = X_train[0].shape




# convert class vectors to binary class matrices
# y_train = keras.utils.to_categorical(y_train, num_classes)
# y_test = keras.utils.to_categorical(y_test, num_classes)

# %matplotlib inline
# this is the size of our encoded representations
encoding_dim = 32  # 32 floats -> compression of factor 24.5, assuming the input is 784 floats

# this is our input placeholder
input_img = Input(shape=(200,))
# "encoded" is the encoded representation of the input
encoded = Dense(encoding_dim, activation='relu')(input_img)
# "decoded" is the lossy reconstruction of the input
decoded = Dense(200, activation='sigmoid')(encoded)

# this model maps an input to its reconstruction
autoencoder = Model(input=input_img, output=decoded)
print("autoencoder model created")

# this model maps an input to its encoded representation
encoder = Model(input=input_img, output=encoded)

# create a placeholder for an encoded (32-dimensional) input
encoded_input = Input(shape=(encoding_dim,))
# retrieve the last layer of the autoencoder model
decoder_layer = autoencoder.layers[-1]
# create the decoder model
decoder = Model(input=encoded_input, output=decoder_layer(encoded_input))

autoencoder.summary()

autoencoder.compile(optimizer='adam', loss='binary_crossentropy')


history = autoencoder.fit(X_train, X_train,
                          batch_size=batch_size, epochs=num_epoch,
                          verbose=1, validation_split=0.2)

# encode and decode some digits
# note that we take them from the *test* set
encoded_imgs = encoder.predict(x_test)
decoded_imgs = decoder.predict(encoded_imgs)

n = 10  # how many digits we will display
fig = plt.figure(figsize=(20, 4))
for i in range(10):
    # display original
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # display reconstruction
    ax = plt.subplot(2, n, i + 1 + n)
    plt.imshow(decoded_imgs[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
# plt.show()
fig.savefig("autoencoded_digits.png")
