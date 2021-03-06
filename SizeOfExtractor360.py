import firebase_admin
from firebase_admin import *
from firebase_admin import firestore
from datetime import datetime
import datetime
import google.cloud

def MiBToBytes_Conversion(mib):
    One_mib_in_bytes=1049000.0
    converted_bytes=mib*One_mib_in_bytes
    return converted_bytes

def BytesToMiB_Conversion(mib_bytes):
    One_mib_in_bytes=1049000.0
    converted_mib=mib_bytes/One_mib_in_bytes
    return converted_mib

def utf8len(s):
    return 1+len(s.encode('utf-8'))#returns 1+utf-8 in accordance to https://firebase.google.com/docs/firestore/storage-size

additionalBytes=16
cred1=credentials.Certificate("project1-4e7b7-firebase-adminsdk-7irgt-433da006ab.json")

def extractDatabase(cred):
    app=firebase_admin.initialize_app(cred)
    db=firestore.client()
    delete_app(app)
    return db
db1=extractDatabase(cred1)

def ExtractRandomDocIdFromCollectionAndPutIntoArray(reference,database):
    docs,array=reference.get(),[]
    for doc in docs:
        array.append(doc.id)
    return array

def SizeAccordingToType(types,size=0):#right now accounts for int,str,bool,list,map,null,datetime,timestamp,reference
    if type(types)==datetime.datetime:
        size=8
    elif type(types)==None:
        size=1
    if type(types)==int or type(types)==float:
        size=8
    elif type(types)==str:
        size=utf8len(types)
    elif type(types) in [True,False]:
        size=1
    elif type(types)==dict:
        for key,value in types.items():
            size+=(SizeAccordingToType(value)+SizeAccordingToType(key))
    elif type(types)==list:
        for t in types:
            size+=SizeAccordingToType(t)#recursive so need to set maximum recursive depth
    return size

pathsOfRandomDocs=[]

MainCollectionUsersFieldDataSize,SubCollectionUsersFieldDataSize=0,0
for doc in db1.collection('users').get():
    usersDict=doc.to_dict()
    MainCollectionUsersFieldDataSize+=SizeAccordingToType(usersDict)

usersCollection=u'users'
usersArray=ExtractRandomDocIdFromCollectionAndPutIntoArray(db1.collection(usersCollection),db1)
usersCollections=[u'barcode_inventory'
                  ,u'bills'
                  ,u'customers'
                  ,u'speech_inventory']#/users/+919777688639/speech_inventory/DQqctA2wSMslh6v0g0ZK/speechInventoryPrice/1538996042795/records/price
#/users/+919777688639/speech_inventory/DQqctA2wSMslh6v0g0ZK/speechInventoryPrice/1538996042795/records/stock


usersPathForSpeechInventory=[]
usersCollectionRandomDocArray=ExtractRandomDocIdFromCollectionAndPutIntoArray(db1.collection(u'users'),db1)
Counter=0
for id1 in usersCollectionRandomDocArray:
    
    for collection in usersCollections:
        if collection=='users':#detailed analysis in u'users' collection,customers has a payment collection
            continue
        elif collection=='customers':
            u_array1=[]
            for doc in db1.collection(usersCollection).document(id1).collection(collection).get():
                SubCollectionUsersFieldDataSize+=SizeAccordingToType(doc.to_dict())
                u_array1.append(doc.id)

            for id22 in u_array1:
                
                for doc in db1.collection(usersCollection).document(randomId).collection(collection).document(id22).collection(u'payment').get():
                    SubCollectionUsersFieldDataSize+=SizeAccordingToType(doc.to_dict())
                    pathSize=utf8len(usersCollection)+utf8len(randomId)+utf8len(collection)+utf8len(id22)+utf8len('payments')+additionalBytes
                    usersPaths.append(('/'+usersCollection+'/'+randomId+'/'+collection+'/'+id22+'/'+'payments',pathSize))
        else:
            Array=[]
            for doc in db1.collection(usersCollection).document(randomId).collection(collection).get():
                SubCollectionUsersFieldDataSize+=SizeAccordingToType(doc.to_dict())
                Array.append(doc.id)
               
            for randomId2 in Array:
                pathSize=utf8len(usersCollection)+utf8len(randomId)+utf8len(collection)+utf8len(randomId2)+additionalBytes
                usersPaths.append(('/'+usersCollection+'/'+randomId+'/'+collection+'/'+randomId2,pathSize))
#123                   
print(usersPathForSpeechInventory)

TotalUserPathSize=0
for (_,size) in usersPaths:
    TotalUserPathSize+=size
print(TotalUserPathSize+MainCollectionUsersFieldDataSize+SubCollectionUsersFieldDataSize)#2344006=?+5079+1614480
print(MainCollectionUsersFieldDataSize)#5079
print(SubCollectionUsersFieldDataSize)#1614480
print('BytesToMiB_Conversion =>'+str(BytesToMiB_Conversion(MainCollectionUsersFieldDataSize)))    
print('BytesToMiB_Conversion =>'+str(BytesToMiB_Conversion(SubCollectionUsersFieldDataSize)))    
print('BytesToMiB_Conversion =>'+str(BytesToMiB_Conversion(TotalUserPathSize)))

'''
2344006
5079
1614480
BytesToMiB_Conversion =>0.0048417540514775976
BytesToMiB_Conversion =>1.53906577693041

BytesToMiB_Conversion =>0.6906072449952335

'''


