"""
The module is the logic layer for silverback
"""
import re
import my_firebase
import my_pattern


warning_exceed = "Uh....you're trying to deduct more than you registered"
warning_empty = "Uh....You haven't join la."
msg_remove = "OK...I've removed your registration"

class Registration:
    def __init__(self, date, name, count):
        self.date = date
        self.name = name
        self.count = count


"""
join() is for add user to player list on a certain date

OUTPUT
    json data with timestamps

PURPOSE:
    The method checks existing date but don't check existing count for players.
EXAMPLES:
    1. User keep changing their mind for +[1-4], nevertheless only the latest record is kept.
    2. User +1 for a future week, the app will create a new document for the registration.
"""
def join(date_code, attn_name, count):
    doc = my_firebase.collection.document(date_code)
    if doc.get().exists:
        return my_firebase.update_field(date_code, attn_name, count)
        #Will get 500 Internal error when value is the same
    else:
        return my_firebase.add_doc(date_code, attn_name, count)


"""
deduct() adjusts player counts from the player POC

OUTPUT
    json data with timestamps

PURPOSE:
    The method reads existing player count from the POC, operates deduction
EXAMPLES:
    1. current > new -> normal situation
    2. current = new -> remove the node
    3. current < new -> throw back warning, do nothing.
"""
def deduct(date_code, attn_name, new_count):
    #Check current status
    doc = my_firebase.collection.document(date_code)
    doc_dict = doc.get().to_dict()
    current_count = doc_dict["attn_list"][attn_name]["count"]
    try: #assumed that there will be no other error here, need some more exception handling
        if new_count>current_count:
            return warning_exceed
        elif new_count==current_count:
            my_firebase.delete(date_code, attn_name)
            return msg_remove
            #need the actual remove action
        else:
            return my_firebase.update_field(date_code, attn_name, current_count-new_count)
    except:
        return warning_empty

def date_convert(date_string):
    year_string = "2019" #DEFAULT assignment
    check_symbol = re.findall(r"\D", date_string)

    if re.match(my_pattern.convert_date, date_string):
        for s in check_symbol:    
            # print("symbols: {}".format(s))
            date_string = date_string.replace(s, "")
            # print(date_string)
        return year_string+date_string
    else:
        return "Unmatched! {}".format(date_string)

"""
reply() is for LINE bot app usage, 

DEFINITION:
    action: [add|deduct] #string anyway
    date_code: 'yyyymmdd
    attn_name: string
    count: int
"""
def reply(message, user_id):
    #DEFAULT values
    attn_name = user_id    
    date_code = "20191014"
    date_raw = "1014" #or ([這|本|下][週|周])
    action = "add"
    count = 0

    """
    Analyzes message, convert to action, date_code, attn_name, count
    """
    if (re.search(my_pattern.date, message)) or (re.search(my_pattern.week, message)):
        msg_list = message.split(" ")
        date_raw = msg_list[0]
        
        #converting [1-9] to 0[1-9]
        if re.search(my_pattern.month_zero, date_code):
            date_code = "0"+date_code
        if re.search(my_pattern.day_zero, date_code):
            date_code = date_code[:-1]+"0"+date_code[-1:] #remove last digit, append "0", add back last digit

        if msg_list[1][-2] == "+":
            action = "add"
        elif msg_list[1][-2] == "-":
            action = "deduct"
        count = msg_list[1][-1]
    elif re.search(my_pattern.quick, message):
        if message[-2] == "+":
            action = "add"
        elif message[-2] == "-":
            action = "deduct"
        count = message[-1]

    date_code = date_convert(date_raw) #convert date, week to date_code with format: yyyymmdd

    #Route to switch-case based on the translation result
    return {
        'add': lambda date_code, attn_name, count: join(date_code, attn_name, count),
        'deduct': lambda date_code, attn_name, count: deduct(date_code, attn_name, count)
    }[action](date_code, attn_name, count)