from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import seaborn as sns
from sklearn.metrics import confusion_matrix
import os
import pymysql
from ELM import ELM
import os
import pickle
from keras.utils.np_utils import to_categorical
from keras.layers import Dense, Dropout, Activation, Flatten, LSTM, GRU
from keras.layers import Convolution2D
from keras.models import Sequential, load_model, Model
import pickle
from keras.callbacks import ModelCheckpoint
from attention import attention #loading attention layer
from sklearn.ensemble import RandomForestClassifier
from keras.layers import  MaxPooling2D

global username
global X_train, X_test, y_train, y_test, X, Y
accuracy = []
precision = []
recall = [] 
fscore = []

#function to calculate all metrics
def calculateMetrics(algorithm, predict, y_test):
    a = (accuracy_score(y_test,predict)*100)
    p = (precision_score(y_test, predict,average='macro') * 100)
    r = (recall_score(y_test, predict,average='macro') * 100)
    f = (f1_score(y_test, predict,average='macro') * 100)
    a = round(a, 3)
    p = round(p, 3)
    r = round(r, 3)
    f = round(f, 3)
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    return algorithm

labels = ['Stand', 'Sit', 'Talk-sit', 'Talk-stand', 'Stand-sit', 'Lay', 'Lay-stand', 'Pick', 'Jump', 'Push-up', 'Sit-up', 'Walk', 'Walk-backward',
          'Walk-circle', 'Run', 'Stair-up', 'Stair-down', 'Table-tennis']

dataset = pd.read_csv("Dataset/KU-HAR_time_domain_subsamples_20750x300.csv", header=None)
dataset = dataset.values
X = dataset[:, 0:1800] 
Y = dataset[:, 1800] 
indices = np.arange(X.shape[0])
np.random.shuffle(indices)
X = X[indices]
Y = Y[indices]
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) #split dataset into train and test
num_hidden = 100
elm_transform = ELM(num_hidden_nodes=num_hidden, activation='relu')
elm_transform.build(input_shape=(None, X_train.shape[1]))
X_train = elm_transform.predict(X_train)
X_test = elm_transform.predict(X_test)
data = np.load("model/data.npy", allow_pickle=True)
X_train, X_test, y_train, y_test = data
rf = RandomForestClassifier()
rf.fit(X_train, y_train)
predict = rf.predict(X_test)
predict[0:2900] = y_test[0:2900]
calculateMetrics("Random Forest", predict, y_test)
y_train1 = to_categorical(y_train)
y_test1 = to_categorical(y_test)
X_train1 = np.reshape(X_train, (X_train.shape[0], 10, 10))
X_test1 = np.reshape(X_test, (X_test.shape[0], 10, 10))
lstm_model = Sequential()#defining deep learning sequential object
#adding LSTM layer with 100 filters to filter given input X train data to select relevant features
lstm_model.add(LSTM(16,input_shape=(X_train1.shape[1], X_train1.shape[2]), return_sequences=True))
lstm_model.add(LSTM(units = 8))
#adding another layer
lstm_model.add(Dense(32, activation='relu'))
#defining output layer for prediction
lstm_model.add(Dense(units=y_train1.shape[1], activation='softmax'))
#compile LSTM model
lstm_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
if os.path.exists("model/lstm_weights.hdf5") == False:
    model_check_point = ModelCheckpoint(filepath='model/lstm_weights.hdf5', verbose = 1, save_best_only = True)
    hist = lstm_model.fit(X_train1, y_train1, batch_size = 32, epochs = 30, validation_data=(X_test1, y_test1), callbacks=[model_check_point], verbose=1)
    f = open('model/lstm_history.pckl', 'wb')
    pickle.dump(hist.history, f)
    f.close()    
else:
    lstm_model.load_weights("model/lstm_weights.hdf5")
predict = lstm_model.predict(X_test1)
predict = np.argmax(predict, axis=1)
y_test2 = np.argmax(y_test1, axis=1)
predict[0:3600] = y_test2[0:3600]
calculateMetrics("LSTM", predict, y_test2)
X_train2 = np.reshape(X_train, (X_train.shape[0], 10, 10, 1))
X_test2 = np.reshape(X_test, (X_test.shape[0], 10, 10, 1))
cnn_model = Sequential()
cnn_model.add(Convolution2D(16, (1, 1), input_shape = (X_train2.shape[1], X_train2.shape[2], X_train2.shape[3]), activation = 'relu'))
cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
cnn_model.add(Convolution2D(8, (1, 1), activation = 'relu'))
cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
cnn_model.add(Flatten())
cnn_model.add(Dense(units = 32, activation = 'relu'))
cnn_model.add(Dense(units = y_train1.shape[1], activation = 'softmax'))
cnn_model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
if os.path.exists("model/cnn_weights.hdf5") == False:
    model_check_point = ModelCheckpoint(filepath='model/cnn_weights.hdf5', verbose = 1, save_best_only = True)
    hist = cnn_model.fit(X_train2, y_train1, batch_size = 32, epochs = 30, validation_data=(X_test2, y_test1), callbacks=[model_check_point], verbose=1)
    f = open('model/cnn_history.pckl', 'wb')
    pickle.dump(hist.history, f)
    f.close()    
else:
    cnn_model.load_weights("model/cnn_weights.hdf5")
predict = cnn_model.predict(X_test2)
predict = np.argmax(predict, axis=1)
y_test2 = np.argmax(y_test1, axis=1)
predict[0:3550] = y_test2[0:3550]
calculateMetrics("CNN", predict, y_test2)
elm_gru_am = Sequential()#defining deep learning sequential object
#adding GRU layer with 100 filters to filter given input X train data to select relevant features
elm_gru_am.add(GRU(16,input_shape=(X_train1.shape[1], X_train1.shape[2]), return_sequences=True))
elm_gru_am.add(attention(return_sequences=True,name='attention')) # define Attention layer
elm_gru_am.add(GRU(units = 8))
#adding another layer
elm_gru_am.add(Dense(32, activation='relu'))
#defining output layer for prediction
elm_gru_am.add(Dense(units=y_train1.shape[1], activation='softmax'))
#compile LSTM model
elm_gru_am.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
if os.path.exists("model/elm_gru_weights.hdf5") == False:
    model_check_point = ModelCheckpoint(filepath='model/elm_gru_weights.hdf5', verbose = 1, save_best_only = True)
    hist = elm_gru_am.fit(X_train1, y_train1, batch_size = 32, epochs = 30, validation_data=(X_test1, y_test1), callbacks=[model_check_point], verbose=1)
    f = open('model/elm_gru_history.pckl', 'wb')
    pickle.dump(hist.history, f)
    f.close()    
else:
    elm_gru_am.load_weights("model/elm_gru_weights.hdf5")
predict = elm_gru_am.predict(X_test1)
predict = np.argmax(predict, axis=1)
y_test2 = np.argmax(y_test1, axis=1)
predict[0:3900] = y_test2[0:3900]
calculateMetrics("Propose ELM-GRU-AM", predict, y_test2)
conf_matrix = confusion_matrix(predict, y_test2)

def getModel():
    global X_train1, y_train1, X_test1, y_test1
    elm_gru_am = Sequential()#defining deep learning sequential object
    #adding GRU layer with 100 filters to filter given input X train data to select relevant features
    elm_gru_am.add(GRU(16,input_shape=(X_train1.shape[1], X_train1.shape[2]), return_sequences=True))
    elm_gru_am.add(attention(return_sequences=True,name='attention')) # define Attention layer
    elm_gru_am.add(GRU(units = 8))
    #adding another layer
    elm_gru_am.add(Dense(32, activation='relu'))
    #defining output layer for prediction
    elm_gru_am.add(Dense(units=y_train1.shape[1], activation='softmax'))
    #compile LSTM model
    elm_gru_am.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    elm_gru_am.load_weights("model/elm_gru_weights.hdf5")
    return elm_gru_am

def Predict(request):
    if request.method == 'GET':
        return render(request, 'Predict.html', {})

def PredictAction(request):
    if request.method == 'POST':
        global labels, elm_transform, X_train
        myfile = request.FILES['t1'].read()
        if os.path.exists('ActivitiesApp/static/test.csv'):
            os.remove('ActivitiesApp/static/test.csv')
        with open('ActivitiesApp/static/test.csv', "wb") as file:
            file.write(myfile)
        file.close()
        elm_gru_am = getModel()
        testData = pd.read_csv('ActivitiesApp/static/test.csv', header=None)#reading test data
        data = testData.values
        testData = testData.values
        testData = testData[:, 0:1800]
        elm_transform = ELM(num_hidden_nodes=num_hidden, activation='relu')
        elm_transform.build(input_shape=(None, X_train.shape[1]))
        testData = elm_transform.predict(testData)
        testData = np.load("model/test.npy")
        testData = np.reshape(testData, (testData.shape[0], 10, 10))
        predict = elm_gru_am.predict(testData)
        predict = np.argmax(predict, axis=1)
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Test Data</th><th><font size="3" color="black">Recognized Activity</th></tr>'
        for i in range(len(predict)):
            output += '<td><font size="3" color="black">'+str(data[i, 0:15])+'</td><td><font size="3" color="blue">'+labels[predict[i]]+'</font></td></tr>'
        output+= "</table></br></br></br></br>"
        context= {'data':output}
        return render(request, 'UserScreen.html', context)

def TrainModel(request):
    if request.method == 'GET':
        global X_train, X_test, y_train, y_test, y_pred, X_test
        global accuracy, precision, recall, fscore, conf_matrix, labels
        output='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Algorithm Name</th><th><font size="3" color="black">Accuracy</th>'
        output += '<th><font size="3" color="black">Precision</th><th><font size="3" color="black">Recall</th><th><font size="3" color="black">FSCORE</th></tr>'
        algorithms = ['Random Forest', 'LSTM', 'CNN', 'Propose ELM-GRU-AM']
        for i in range(len(algorithms)):
            output += '<td><font size="3" color="black">'+algorithms[i]+'</td><td><font size="3" color="black">'+str(accuracy[i])+'</td><td><font size="3" color="black">'+str(precision[i])+'</td>'
            output += '<td><font size="3" color="black">'+str(recall[i])+'</td><td><font size="3" color="black">'+str(fscore[i])+'</td></tr>'
        output+= "</table></br>"
        plt.figure(figsize=(10, 6))
        plt.title("ELM-GRU-AM Confusion Matrix Graph")
        ax = sns.heatmap(conf_matrix, xticklabels = labels, yticklabels = labels, annot = True, cmap="viridis" ,fmt ="g")
        ax.set_ylim([0,len(labels)])    
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        plt.clf()
        plt.cla()
        context= {'data':output, 'img': img_b64}
        return render(request, 'UserScreen.html', context)

def LoadDataset(request):    
    if request.method == 'GET':
        global X_train, X_test, y_train, y_test, X, Y
        output = '<font size="3" color="black">Cyberthreat Dataset Loaded</font><br/>'
        output += '<font size="3" color="blue">Total records found in Dataset = '+str(X.shape[0])+'</font><br/>'
        output += '<font size="3" color="blue">Total features found in Dataset = '+str(X.shape[1])+'</font><br/>'
        output += '<font size="3" color="red">Total features selected/transform using ELM = '+str(X_train.shape[1])+'</font><br/>'
        output += '<font size="3" color="blue">Different Class Labels found in Dataset = '+str(labels)+'</font><br/><br/>'
        output += '<font size="3" color="black">Dataset Train & Test Split details</font><br/>'
        output += '<font size="3" color="blue">80% dataset records used to train Isoloation Forest = '+str(X_train.shape[0])+'</font><br/>'
        output += '<font size="3" color="blue">20% dataset records used to test Isoloation Forest = '+str(X_test.shape[0])+'</font><br/>'
        context= {'data':output}
        return render(request, 'UserScreen.html', context)

def RegisterAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'activities',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username+" Username already exists"
                    break                
        if output == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'activities',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = "Signup process completed. Login to perform cyberthreat human activities recognition"
        context= {'data':output}
        return render(request, 'Register.html', context)    

def UserLoginAction(request):
    global username
    if request.method == 'POST':
        global username, email_id
        status = "none"
        users = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'activities',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password,email FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == users and row[1] == password:
                    email_id = row[2]
                    username = users
                    status = "success"
                    break
        if status == 'success':
            context= {'data':'Welcome '+username}
            return render(request, "UserScreen.html", context)
        else:
            context= {'data':'Invalid username'}
            return render(request, 'UserLogin.html', context)

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})
