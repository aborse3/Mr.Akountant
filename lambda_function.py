import json
from datetime import datetime
import base64
import jwt
from jwt.algorithms import RSAAlgorithm
import psycopg2
from config import config
from dateutil import parser

def lambda_handler(event, context):
    # TODO implement
    request_body = json.loads(event['body'])
    print request_body
    id_token = str(request_body['originalDetectIntentRequest']['payload']['user']['idToken'])
    params = request_body['queryResult']['parameters']
    print params
    #{'Action': 'add', 'unit-currency': {'amount': 20.0, 'currency': 'USD'}, 'category': 'movies'}
    user_details = get_user_details_from_token(id_token)
    #print(user_details)

    if params['Action'] == 'add':
        response=add_expense(params,user_details,0)
    elif params['Action'] == 'delete':
        response=add_expense(params,user_details,1)
    elif params['Action'] == 'spend':
        response=get_expense(params,user_details)
    else:
        print "NO ACTION MATCHED"
    print response
    return {

        "statusCode": 200,
        "body": json.dumps({"fulfillmentText": response})
    }

def add_expense(params,user_details,delete_flag):
    print "inside add"
    Amount=params['unit-currency']['amount'];
    Amount_num=float(Amount)
    if(delete_flag==1):
        Amount_num=Amount_num*-1
    Amount=str(Amount_num)
    insert_query_json={
        "Email_ID":user_details['email'],
        "First_Name":user_details['given_name'],
        "Last_Name":user_details['family_name'],
        "Date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Etype" : params['category'],
        "Amount" : Amount,
        "Currency" : params['unit-currency']['currency']
    }
    print insert_query_json
    insert_query(insert_query_json)
    if(delete_flag==1):
        action="deleted "
    else:
        action="added "
    return action+str(params['unit-currency']['amount'])+" "+str(params['unit-currency']['currency'])+" to "+str(params['category'])

def insert_query(json1):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO expenses(Email_ID,First_Name,Last_Name,Date,Etype,Amount,Currency)
             VALUES(%s,%s,%s,%s,%s,%s,%s) ;"""
    conn = None
    users_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (json1["Email_ID"],json1["First_Name"],json1["Last_Name"],json1["Date"],json1["Etype"],json1["Amount"],json1["Currency"]))
        # get the generated id back
        print "asdf"
        '''users_id = cur.fetchone()[0]'''
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def fire_get_query_start_end(sql,Email_ID,category,start_date,end_date):
    #sql="select * from expenses"
    conn = None
    users_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        #if(category is NONE):
        if(category!=''):
            cur.execute(sql, (Email_ID,category,start_date,end_date))
        else:
            cur.execute(sql, (Email_ID,start_date,end_date))
        #else:
        #    cur.execute(sql, (Email_ID,start_date,end_date,category))

        SUM= cur.fetchone()[0]
        # get the generated id back
        print "asdf"
        '''users_id = cur.fetchone()[0]'''
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return SUM

def fire_get_query(sql,Email_ID,category):
    #sql="select * from expenses"
    conn = None
    users_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        #if(category is NONE):
        if(category!=''):
            cur.execute(sql, (Email_ID,category))
        else:
            cur.execute(sql, (Email_ID,))
        #else:
        #    cur.execute(sql, (Email_ID,start_date,end_date,category))

        SUM= cur.fetchone()[0]
        # get the generated id back
        print "asdf"
        '''users_id = cur.fetchone()[0]'''
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return SUM


def get_expense(params,user_details):
    category=""
    if(params['date-period']!=''):
        datetime_object_start = parser.parse(params['date-period']['startDate'])
        datetime_object_end = parser.parse(params['date-period']['endDate'])
        datetime_object_start=datetime_object_start.replace(hour=00,minute=00,second=00)
        datetime_object_end=datetime_object_end.repxnlace(hour=23,minute=59,second=59)
        print datetime_object_start
        print datetime_object_end
        datetime_object_start=datetime_object_start.strftime("%Y-%m-%d %H:%M:%S")
        datetime_object_end=datetime_object_end.strftime("%Y-%m-%d %H:%M:%S")
        if(params['category']!=''):
            sql = """SELECT SUM(AMOUNT) from expenses where Email_ID=%s and Etype=%s and date between %s and %s;"""
            SUM = fire_get_query_start_end(sql,user_details['email'],params['category'],datetime_object_start,datetime_object_end)
            category=" on "+params['category']
        else:
            sql = """SELECT SUM(AMOUNT) from expenses where Email_ID=%s and date between %s and %s;"""
            SUM = fire_get_query_start_end(sql,user_details['email'],'',datetime_object_start,datetime_object_end)
    elif(params['date-period']=='' and params['date']!=''):
        datetime_object_start = parser.parse(params['date'])
        print datetime_object_start
        datetime_object_end=datetime_object_start
        datetime_object_start=datetime_object_end.replace(hour=00,minute=00,second=00)
        datetime_object_end=datetime_object_end.replace(hour=23,minute=59,second=59)
        print datetime_object_end
        datetime_object_start=datetime_object_start.strftime("%Y-%m-%d %H:%M:%S")
        datetime_object_end=datetime_object_end.strftime("%Y-%m-%d %H:%M:%S")
        if(params['category']!=''):
            sql = """SELECT SUM(AMOUNT) from expenses where Email_ID=%s and Etype=%s and date between %s and %s;"""
            SUM = fire_get_query_start_end(sql,user_details['email'],params['category'],datetime_object_start,datetime_object_end)
            category=" on "+params['category']
        else:
            sql = """SELECT SUM(AMOUNT) from expenses where Email_ID=%s and date between %s and %s;"""
            SUM = fire_get_query_start_end(sql,user_details['email'],'',datetime_object_start,datetime_object_end)
    elif(params['date-period']=='' and params['date']==''):
        if(params['category']!=''):
            sql = """SELECT SUM(AMOUNT) from expenses where Email_ID=%s and Etype=%s ;"""
            SUM = fire_get_query(sql,user_details['email'],params['category'])
            category=" on "+params['category']
        else:
            sql = """SELECT SUM(AMOUNT) from expenses where Email_ID=%s;"""
            SUM = fire_get_query(sql,user_details['email'],'')
    if SUM is None:
        SUM=str(0);
    return "You spent "+str(SUM)+" dollars"+category

def get_user_details_from_token(encoded):
    #this function gives decoded JSONified user data
    key_json ="""{
      "kid": "728f4016652079b9ed99861bb09bafc5a45baa86",
      "e": "AQAB",
      "kty": "RSA",
      "alg": "RS256",
      "n": "sbRNoYaZX3w2Iosb6uzfykt-uJh_NRVQ0h_98Gptkpq3r-xgdaq9i-mmZEYZtrNUmIqOEDvtIJ36-CVnDZI2p_eARFkmedHC14QX5SHdFb2qr0a5DuqC5qLoyOMXSNJyfRHK8ULjozLxO7t_P0EsdlLPOUQjcbpTiIo9p-L9iskMCKpQdDfQ4CrzHKQjfYN3KJdehsChguffue-VBUkoDaRRUA50h6DiFe-loC_dzycoNGYJEJvAM5DC3zuHr6dfc5saHLUi4upgR2_jchA6kwSOVBC05qUgY4E3UdYTWciTqkSowiAErDx21g-oB6QzIr8MRMzKa89-g2Ine-qE7Q",
      "use": "sig"
    }"""

    coded_string = encoded.split('.')[0]
    public_key_slack="""{
      "keys": [
        {
          "e": "AQAB",
          "kty": "RSA",
          "alg": "RS256",
          "n": "3DtaPxVC9Nd8pEn-Y50eyL5YxF-mT_zLXY_TummZNaczgX_XoXlFiK26FJZ2wf8CMrA4lul8otyEBtcI_sJUSDdw_ngWGNjA4XFnayO-GNwXG4pvfcILn4acO3YyiPdkb4PS6WYCGqVD5PIrnuCeKtX4K28vva8SUGCOiPiysNvoUpNGiqUxiBLWdvD9TJvrrC0QbpdGDPH2kzcHJjLQp3n0tCW6L06slFHufB9MBhlE0lN4egKlcaB4noqUitwv77WXBuWHTQRL431Bn7tzACL-xvvL6wgKqvLTT9FDaKvnEMDhomE1FPLKQEK-mAcNYQl_ro0BaQGPPlGSI76Y9Q",
          "use": "sig",
          "kid": "961cf60bcedd9067c4cf1f2ddf4ed612b536fb1a"
        },
        {
          "kid": "728f4016652079b9ed99861bb09bafc5a45baa86",
          "e": "AQAB",
          "kty": "RSA",
          "alg": "RS256",
          "n": "sbRNoYaZX3w2Iosb6uzfykt-uJh_NRVQ0h_98Gptkpq3r-xgdaq9i-mmZEYZtrNUmIqOEDvtIJ36-CVnDZI2p_eARFkmedHC14QX5SHdFb2qr0a5DuqC5qLoyOMXSNJyfRHK8ULjozLxO7t_P0EsdlLPOUQjcbpTiIo9p-L9iskMCKpQdDfQ4CrzHKQjfYN3KJdehsChguffue-VBUkoDaRRUA50h6DiFe-loC_dzycoNGYJEJvAM5DC3zuHr6dfc5saHLUi4upgR2_jchA6kwSOVBC05qUgY4E3UdYTWciTqkSowiAErDx21g-oB6QzIr8MRMzKa89-g2Ine-qE7Q",
          "use": "sig"
        }
      ]
    }"""
    public_key_slack=json.loads(public_key_slack)

    missing_padding = len(coded_string) % 4
    if missing_padding != 0:
        coded_string += b'='* (4 - missing_padding)

    decoded_string = base64.b64decode(coded_string)

    decoded_json=json.loads(decoded_string)
    if(public_key_slack['keys'][0]['kid']==decoded_json['kid']):
        key_josn=public_key_slack['keys'][0]
    else:
        key_josn=public_key_slack['keys'][1]

    public_key = RSAAlgorithm.from_jwk(key_json)

    decoded = jwt.decode(encoded, public_key, algorithms='RS256',verify=False)
    return decoded
