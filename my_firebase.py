import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials


DEFAULT_MAX = 10

cred = credentials.Certificate('serviceAccount.json')

firebase_admin.initialize_app(cred)
db = firestore.client()
collection = db.collection("events") #Ref Method1
# doc_ref = db.document("/events/20191006") #Ref Method2


"""
Create play date as document
   By calling this method with existing date, all field data will be overitten
"""
def add_doc(date, name, count):
    create_date = collection.document(date)
    doc_data = {
        'attn_list': {name:{'name':name, 'count':count}},
        'max': DEFAULT_MAX
    }
    return create_date.set(doc_data)


#Read doc data
def read_doc(date):
    query_date = collection.document(date)
    doc = query_date.get()

    return "{}".format(doc.to_dict())


#Update field
def update_field(date, name, count):
    update_doc = collection.document(date)
    doc_data = {
        'attn_list': {name:{'name':name, 'count':count}}
    }
    return update_doc.update(doc_data)


def delete(date, name):
    doc_ref = collection.document(date)
    doc = doc_ref.get()
    fields = doc.to_dict()
    del fields['attn_list'][name]
    
    return doc_ref.update(fields)