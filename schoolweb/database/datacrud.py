import boto3
import json
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from . import credentials

# TABLE ACCESS
table = boto3.resource(
        'dynamodb',
        aws_access_key_id= credentials.creds()['accessKey'],
        aws_secret_access_key= credentials.creds()['secretKey'],
        region_name=credentials.creds()['region'],
    ).Table('planner-db')


# GET ITEMS
def get(partition_key, sort_key):
    
    response = None
    try:
        response = table.get_item(
                Key={"planner-pk": partition_key, "planner-sk": sort_key})
    except ClientError as e:
        response = {'error': str(e)}
    return response.get('Item', {}) if response and 'Item' in response else {}

# PUT ITEMS
def put(in_data):
    data = {
        'planner-pk': in_data.get('planner_pk'),
        'planner-sk': in_data.get('planner_sk'),
        'password':in_data.get('password'),
        'name':in_data.get('name'),
        'parent_name': in_data.get('parent_name'),
        'address': in_data.get('address'),
        'age':in_data.get('age'),
        'free-edu':in_data.get('free_edu'),
        'status':in_data.get('status'),
        'emis':in_data.get('emis'),
        'mobile':in_data.get('mobile'),
        'std':in_data.get('std'),
        'dob':in_data.get('dob'),
        'doj':in_data.get('doj'),
        'dol':in_data.get('dol'),
        'fees_paid': in_data.get('fees_paid') or [],
        'bonafide': in_data.get('bonafide') or [],
        'totp_secret': in_data.get('totp_secret', ''),
        'theme': in_data.get('theme', 'light'),
        'designation': in_data.get('designation', ''),
    }

    response = None
    try:
        response = table.put_item(Item = data)
    except ClientError as e:
        response = {'error': str(e)}
    return response
# PUT for Bill Num
def put_bill(in_data):
    data = {
        'planner-pk': in_data.get('planner_pk'),
        'planner-sk': in_data.get('planner_sk'),
        'num':in_data.get('num'),
    }
    response = None
    try:
        response = table.put_item(Item = data)
    except ClientError as e:
        response = {'error': str(e)}
    return response

# PUT for Password Reset
def put_pwd_reset(in_data):
    data = {
        'planner-pk': in_data.get('planner_pk'),
        'planner-sk': in_data.get('planner_sk'),
        'previous_pwd_reset': in_data.get('previous_pwd_reset', []),
        'current_pwd_reset_date': in_data.get('current_pwd_reset_date'),
        'current_reset_status': in_data.get('current_reset_status'),
        'name': in_data.get('name'),
        'target_pk': in_data.get('target_pk')
    }
    response = None
    try:
        response = table.put_item(Item = data)
    except ClientError as e:
        response = {'error': str(e)}
    return response

# PUT for Fee Details
def put_fee(pk, sk, in_data):
    data = {
        'planner-pk': pk,
        'planner-sk': sk
    }
    data.update(in_data)
    response = None
    try:
        response = table.put_item(Item = data)
    except ClientError as e:
        response = {'error': str(e)}
    return response
# UPDATE ITEMS
def update(data):
    pk = "Student"
    sk = data.get('sid')
    updateDict = {}
    updateDict['STD'] = data.get('std')
    updateDict['TERM'] = data.get('term')
    updateDict['FEE_PART'] = data.get('fee_particulars')
    updateDict['AMOUNT'] = data.get('amount_paid')
    updateDict['BILLED_BY'] = data.get('billed_by')
    updateDict['PAYMENT_DATE'] = data.get('payment_date')
    updateDict['BILL_NO'] = data.get('bill_no')
    updateDict['PAYMENT_TYPE'] = data.get('payment_type')
    response = None
    try:
        response = table.update_item(
            Key={'planner-pk': pk, 'planner-sk': sk},
            UpdateExpression="SET #fl = list_append(if_not_exists(#fl, :empty_list), :val)",
            ExpressionAttributeNames={'#fl': 'fees_paid'},
            ExpressionAttributeValues={':val': [updateDict], ':empty_list': []},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        response = {'error': str(e)}
    return response
    
def update_bonafide(pk, sk, cert_data):
    response = None
    try:
        cert_data.pop('profile', None)
        cert_data.pop('cert_num_int', None)
        if 'date' in cert_data:
            cert_data['dateIssued'] = cert_data['date']
            cert_data.pop('date', None)
        response = table.update_item(
            Key={'planner-pk': pk, 'planner-sk': sk},
            UpdateExpression="SET #bl = list_append(if_not_exists(#bl, :empty_list), :val)",
            ExpressionAttributeNames={'#bl': 'bonafide'},
            ExpressionAttributeValues={':val': [cert_data], ':empty_list': []},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        response = {'error': str(e)}
    return response

def put_bonafide_num(num):
    return put_bill({
        'planner_pk': 'BonafideRequests',
        'planner_sk': 'latest',
        'num': num
    })

def scan_by_pk(pk):
    try:
        # Scans the table for a specific partition key (e.g., all vouchers)
        items = []
        exclusive_start_key = None
        while True:
            if exclusive_start_key:
                response = table.scan(
                    FilterExpression=Attr('planner-pk').eq(pk),
                    ExclusiveStartKey=exclusive_start_key
                )
            else:
                response = table.scan(
                    FilterExpression=Attr('planner-pk').eq(pk)
                )

            items.extend(response.get('Items', []))
            exclusive_start_key = response.get('LastEvaluatedKey')
            if not exclusive_start_key:
                break

        return items
    except ClientError as e:
        return {'error': str(e)}

def scan_by_std(std):
    try:
        # Scans the table for all students in a specific grade
        response = table.scan(
            FilterExpression=Attr('planner-pk').eq('Student') & Attr('std').eq(std)
        )
        return response.get('Items', [])
    except ClientError as e:
        return {'error': str(e)}

def scan_by_mobile(profile, mobile):
    try:
        response = table.scan(
            FilterExpression=Attr('planner-pk').eq(profile) & Attr('mobile').eq(mobile)
        )
        return response.get('Items', [])
    except ClientError as e:
        return {'error': str(e)}

def delete(partition_key, sort_key):
    try:
        response = table.delete_item(
            Key={"planner-pk": partition_key, "planner-sk": sort_key})
        return response
    except ClientError as e:
        return {'error': str(e)}
    
def update_status(pk, sk, status, approved_by):
    try:
        # Targeted update to only modify status and approval fields
        response = table.update_item(
            Key={'planner-pk': pk, 'planner-sk': sk},
            UpdateExpression="SET #s = :s, approved_by = :ab",
            ExpressionAttributeNames={
                '#s': 'status'
            },
            ExpressionAttributeValues={
                ':s': status,
                ':ab': approved_by
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except ClientError as e:
        return {'error': str(e)}
