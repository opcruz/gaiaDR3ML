import pandas as pd
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def model_solution():
    #load data
    df = pd.read_csv('spectra_pca_SNG.csv')


    # separate the characteristics (X) and the label (y)
    X = df.drop('id', axis=1)
    y = df['id']

    # encode the label (y)
    encoder = LabelEncoder()
    y = encoder.fit_transform(y)

    # split the dataset into training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=None)

    # create the model

    model = tf.keras.models.Sequential([
      tf.keras.layers.Dense(64, activation='relu'),
      tf.keras.layers.Dropout(0.4),
      tf.keras.layers.Dense(32, activation='relu'),
      tf.keras.layers.Dropout(0.3),
      tf.keras.layers.Dense(3, activation='softmax')
    ])

    # compile the model
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # train the model
    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

    # graphing training and test accuracy
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='test')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

    y = df['id']
    dfEncoder = pd.DataFrame(y)
    dfEncoder['codificado'] = encoder.fit_transform(dfEncoder['id'])

    name_labels = encoder.classes_
    new_names = ['Symbiotics', 'Planetary Nebulae', 'Red Giants']
    name_labels_dict = {name_labels[i]: new_names[i] for i in range(len(name_labels))}
    dfEncoder['nombres_etiquetas'] = dfEncoder['id'].map(name_labels_dict)
    df_agrupado = dfEncoder.groupby('nombres_etiquetas')['codificado'].mean()
    print(df_agrupado)


    # predicting probabilities for test data
    y_probs = model.predict(X_test)

    # convert probabilities into labels
    y_pred = np.argmax(y_probs, axis=-1)

    # obtain the confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print()
    print("CONFUSION MATRIX")
    print(cm)

    # obtain the predictions for the test data
    y_pred = np.argmax(model.predict(X_test), axis=-1)

    # obtain the classification report
    report = classification_report(y_test, y_pred, digits=4)
    print()
    print("CLASSIFICATION REPORT")
    print(report)

    #print accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print('Accuracy:', accuracy)

    print()
    print("size of the splits")
    print("X_train: ", X_train.shape)
    print("X_test: ", X_test.shape)
    print("y_test: ", y_test.size)
    print("y_pred: ", y_pred.size)

    return model


# Note that you'll need to save your model as a .h5 like this.

if __name__ == '__main__':
    model = model_solution()
    model.save('RNA_SNG.h5')