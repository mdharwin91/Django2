from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password
from django.template import loader
from .forms import InputForm, LoginForm, StudentInfo, StudentInfoFetch
from .model import models
from .model.models import schoolInformation
from .authen import loginauth
from .database import credentials,datacrud
from django.views.decorators.csrf import csrf_exempt
import json
import pyotp
from datetime import datetime, date
import base64
import re, html
import requests
from urllib.parse import quote

def sanitize_str(s):
    if s is None:
        return ''
    if not isinstance(s, str):
        s = str(s)
    # Unescape HTML entities
    s = html.unescape(s)
    # Remove HTML tags
    s = re.sub(r'<[^>]*>', '', s)
    # Remove common incomplete fragments left after tag-stripping
    for frag in ['input type=', 'div id=', 'select name=', 'option value=', 'name=', 'value=', 'readonly']:
        s = s.replace(frag, '')
    # Remove stray angle brackets and quotes
    s = s.replace('<', '').replace('>', '')
    s = s.replace('"', '').replace("'", '')
    return s.strip()

def donation_page(request):
    schoolInformation = models.schoolInformation
    return render (request, 'donation.html', {'schoolInformation' : schoolInformation})

def main_page(request):
    schoolInformation = models.schoolInformation
    return render(request, 'main.html', {'schoolInformation': schoolInformation})

def common_page(request):
    user_session = request.session.get('user')
    if not user_session or user_session == "ACCESS DENIED" or (isinstance(user_session, dict) and (user_session.get('user') == "ACCESS DENIED" or not user_session.get('user'))):
        return redirect('/login/')

    profile_info = {}
    # Fetch full user details from database
    pk = user_session.get('pk')
    sk = user_session.get('sk')
    if pk and sk:
        db_data = datacrud.get(pk, sk)
        if db_data:
            profile_info = studentObjMap(db_data)

    schoolInformation = models.schoolInformation
    return render (request, 'common.html', {
        'schoolInformation' : schoolInformation,
        'profile_info': profile_info
    })

def header_page(request):
    schoolInformation = models.schoolInformation
    return render (request, 'header.html', {'schoolInformation' : schoolInformation})

def say_sec_hello(request):
    schoolInformation = models.schoolInformation
    return render (request, 'about.html', {'schoolInformation' : schoolInformation})

def default_page(request):
    schoolInformation = models.schoolInformation
    context = {}
    context['form'] = InputForm()
    context['schoolInformation'] = schoolInformation
    return render(request, "default.html", context)

def admin_page(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    if isinstance(user, dict) and user.get('pk') != 'Admin':
        return redirect('/login/')
    schoolInformation = models.schoolInformation
    return render (request, 'adminpage.html', {
        'schoolInformation' : schoolInformation, 
        'standards': models.SchoolStandard, 
        'feeNames': models.feeNames, 
        'profiles': models.profile, 
        'bonafide_msg': models.bonafide_msg,
        'statuses': models.Status,
        'free_edu_choices': models.free_edu
    })
  
def contact_us(request):
    schoolInformation = models.schoolInformation
    return render(request, "contact.html", {'schoolInformation' : schoolInformation})


def login_page(request):

    header_page(request)
    context = {}
    form = LoginForm()
    context['login_info'] = form
    context['schoolInformation'] = models.schoolInformation
    if request.method == 'POST':
        try:
            form = LoginForm(request.POST)
            # Allow the password to be re-rendered into the HTML for the 2FA step
            form.fields['password'].widget.render_value = True
            context['login_info'] = form

            val_01 = form.data.get('username')
            val_02 = form.data.get('password')
            val_otp = request.POST.get('otp_token')

            user_val = loginauth.loginauth.logon(val_01, val_02)
            
            if (user_val.get('user') and user_val['user'] != "ACCESS DENIED"):
                # Check for 2FA
                db_user = datacrud.get(user_val['pk'], user_val['sk'])
                otp_secret = db_user.get('totp_secret')

                if otp_secret:
                    if not val_otp:
                        context['show_otp'] = True
                        context['result'] = "Please enter your 2FA code"
                        return render(request, "login.html", context)
                    
                    totp = pyotp.TOTP(otp_secret)
                    if not totp.verify(val_otp):
                        context['result'] = "Invalid 2FA code"
                        return render(request, "login.html", context)

                request.session['user'] = user_val
                return redirect('/common/')
            else:
                context['result'] = "Login Failed"
                return render(request, "login.html", context)
        except Exception as e:
            pass
    return render(request, "login.html", context)

def logout_page(request):
    """
    Clears the user session and redirects to the login page.
    """
    try:
        # Delete the user key from the session
        del request.session['user']
    except KeyError:
        # If the key doesn't exist, do nothing
        pass
    return redirect('/login/')

def student_details(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    schoolInformation = models.schoolInformation
    context = {}
    # Use empty dicts for template rendering to avoid inserting
    # form-field HTML into input `value` attributes on initial load.
    context['user_info'] = {}
    context['user_info_get'] = {}
    # Provide profile choices from models for the template select
    context['profiles'] = models.profile
    # Provide standards and free-edu choices from models
    context['statuses'] = models.Status
    context['standards'] = models.SchoolStandard
    context['free_edu_choices'] = models.free_edu
    context['schoolInformation'] = models.schoolInformation
    user_session = request.session.get('user')
    if user_session and isinstance(user_session, dict):
        context['current_user_role'] = user_session.get('pk')

    if request.method == 'POST':
        try:
            val_01 = request.POST.get('name')
            val_02 = request.POST.get('planner_sk')
            
            if True:
                    # After POST save, do not pass the form class to template (avoid HTML in inputs)
                context['user_info'] = {}
                # context['user_info'] = datacrud.get("Student")
                # Sanitize POST data before saving to DB
                post = request.POST
                if val_02 == "SID00000" or val_02 == "SID0000" or val_02 == "TID0000" or val_02 == "AID0000" or val_02 == "":
                    context['result'] = "Invalid ID"
                    return render(request, "studentprofile.html", context)
                # Date Validations
                dob_str = post.get('dob')
                doj_str = post.get('doj')
                
                if dob_str:
                    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    # Rule: Profile must be at least 3 years old relative to today
                    if dob_date > date.today().replace(year=date.today().year - 3):
                        context['result'] = "Error: Person must be at least 3 years old."
                        return render(request, "studentprofile.html", context)
                    
                    # Rule: DOJ must be >= DOB + 3 years
                    if doj_str:
                        doj_date = datetime.strptime(doj_str, '%Y-%m-%d').date()
                        try:
                            min_doj = dob_date.replace(year=dob_date.year + 3)
                        except ValueError:
                            # Handle Leap Year (Feb 29) + 3 years
                            min_doj = dob_date.replace(year=dob_date.year + 3, month=3, day=1)
                        
                        if doj_date < min_doj:
                            context['result'] = "Error: Date of Joining must be at least 3 years after Date of Birth."
                            return render(request, "studentprofile.html", context)

                # Server-side validation for Mobile (exactly 10 digits)
                mobile_val = post.get('mobile')
                if mobile_val and not re.fullmatch(r'\d{10}', mobile_val):
                    context['result'] = "Error: Mobile number must be exactly 10 digits."
                    return render(request, "studentprofile.html", context)

                planner_pk = sanitize_str(post.get('planner_pk') or post.get('planner-pk') or '')
                planner_sk = sanitize_str(post.get('planner_sk') or post.get('planner-sk') or '')
                
                # Pad numeric part to 4 digits and ensure prefix is present
                if planner_pk == "Teacher":
                    clean_sk = planner_sk[3:] if planner_sk.startswith("TID") else planner_sk
                    planner_sk = "TID" + clean_sk.zfill(4)
                elif planner_pk == "Student":
                    clean_sk = planner_sk[3:] if planner_sk.startswith("SID") else planner_sk
                    planner_sk = "SID" + clean_sk.zfill(5)
                elif planner_pk == "Admin":
                    clean_sk = planner_sk[3:] if planner_sk.startswith("AID") else planner_sk
                    planner_sk = "AID" + clean_sk.zfill(4)

                # Password Logic: Preserve existing password
                password_to_store = ''
                fees_paid_store = []
                bonafide_store = []

                existing_rec = datacrud.get(planner_pk, planner_sk)
                if existing_rec:
                    password_to_store = existing_rec.get('password', '')
                    fees_paid_store = existing_rec.get('fees_paid') or []
                    bonafide_store = existing_rec.get('bonafide') or []
                else:
                    # Logic for new profiles dynamic password
                    raw_name = sanitize_str(post.get('name') or '')
                    dob_str = post.get('dob') or ''
                    if planner_pk in ['Teacher', 'Admin'] and raw_name and dob_str:
                        # First 4 chars of name in caps + year of birth from DOB (YYYY-MM-DD)
                        name_part = re.sub(r'[^a-zA-Z]', '', raw_name)[:4].upper()
                        year_part = dob_str.split('-')[0]
                        password_to_store = make_password(name_part + year_part)
                    else:
                        password_to_store = make_password('')

                save_data = {
                    'planner_pk': planner_pk,
                    'planner_sk': planner_sk,
                    'name': sanitize_str(post.get('name') or ''),
                    'parent_name': sanitize_str(post.get('parent_name') or ''),
                    'address': sanitize_str(post.get('address') or ''),
                    'age': sanitize_str(post.get('age') or ''),
                    'free_edu': sanitize_str(post.get('free_edu') or post.get('free-edu') or ''),
                    'status': sanitize_str(post.get('status') or ''),
                    'emis': sanitize_str(post.get('emis') or ''),
                    'mobile': sanitize_str(post.get('mobile') or ''),
                    'std': sanitize_str(post.get('std') or ''),
                    'dob': sanitize_str(post.get('dob') or ''),
                    'doj': sanitize_str(post.get('doj') or ''),
                    'dol': sanitize_str(post.get('dol') or ''),
                    'password': password_to_store,
                    'fees_paid': fees_paid_store,
                    'bonafide': bonafide_store,
                }
                datacrud.put(save_data)
                # Pass the saved data back to context so fields remain populated
                context['user_info'] = save_data
                context['result'] = "Data saved successfully"
                return render(request, "studentprofile.html", context)
            else:
                context['result'] = "Login Failed"
                return render(request, "studentprofile.html", context)
        except Exception as e:
            pass
    return render(request, "studentprofile.html", context)

@csrf_exempt 
def student_get(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return JsonResponse({'error': 'Session expired. Please login again.'}, status=401)
    context = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            val_01 = data.get("planner_pk")
            planner_sk = (data.get("planner_sk") or "").strip()
            planner_sk_upper = planner_sk.upper()
            if val_01 == "Teacher":
                clean_sk = planner_sk[3:] if planner_sk_upper.startswith("TID") else planner_sk
                val_02 = "TID" + clean_sk.zfill(4)
            elif val_01 == "Student":
                clean_sk = planner_sk[3:] if planner_sk_upper.startswith("SID") else planner_sk
                val_02 = "SID" + clean_sk.zfill(5)
            elif val_01 == "Admin":
                clean_sk = planner_sk[3:] if planner_sk_upper.startswith("AID") else planner_sk
                val_02 = "AID" + clean_sk.zfill(4)
            elif val_01 == "Enquiry":
                mobile = data.get("mobile")
                if mobile:
                    results = datacrud.scan_by_mobile("Enquiry", mobile)
                    if results and len(results) > 0:
                        return JsonResponse({'user_info': studentObjMap(results[0])})
                    return JsonResponse({'error': 'No enquiry found with this mobile number'}, status=404)
                val_02 = planner_sk
            elif val_01 == "vouchers":
                mobile = data.get("mobile")
                if mobile:
                    results = datacrud.scan_by_mobile("vouchers", mobile)
                    if results and len(results) > 0:
                        info = studentObjMap(results[0])
                        info['voucher_no'] = results[0].get('planner-sk')
                        return JsonResponse({'user_info': info})
                    return JsonResponse({'error': 'No voucher found with this mobile number'}, status=404)

                # Format Voucher ID (e.g., 1 -> VOU00001) if numeric input is 5 digits or less
                clean_sk = planner_sk[3:] if planner_sk.startswith("VOU") else planner_sk
                if clean_sk.isdigit() and len(clean_sk) <= 5:
                    val_02 = "VOU" + clean_sk.zfill(5)
                else:
                    val_02 = planner_sk
            elif val_01 == "bonafide_num":
                responseData = datacrud.get('bonafideCertificate', 'latest_cert')
                current_num = 0
                if responseData and 'num' in responseData:
                    try:
                        current_num = int(responseData['num'])
                    except (ValueError, TypeError):
                        pass
                return JsonResponse({'success': True, 'next_num': current_num + 1})
            elif val_01 == "voucher_num":
                responseData = datacrud.get('vouchers', 'latest')
                current_num = 0
                if responseData and 'num' in responseData:
                    try:
                        current_num = int(responseData['num'])
                    except (ValueError, TypeError):
                        pass
                return JsonResponse({'success': True, 'next_num': current_num + 1})
            elif val_01 == "Bulk":
                # Fetch all students in a standard for WhatsApp bulk messaging
                responseData = datacrud.scan_by_std(planner_sk)
                if isinstance(responseData, list):
                    students = [studentObjMap(item) for item in responseData]
                    return JsonResponse({'success': True, 'students': students})
                else:
                    return JsonResponse({'success': False, 'error': 'Failed to fetch students'}, status=500)
            
            print("Name: ",val_01, " ", val_02)
            if val_01 and val_02:
                responseData = datacrud.get(val_01, val_02)
                print("Response: ", responseData)
                if responseData:
                    student_info = studentObjMap(responseData)
                    # If it's a voucher, ensure simple mapping for frontend
                    if val_01 == "vouchers":
                        student_info['voucher_no'] = responseData.get('planner-sk')
                    
                    # Fetch Bonafide requests for this profile to include pending ones
                    if val_01 in ["Student", "Teacher", "Admin"]:
                        try:
                            bonafide_reqs = datacrud.scan_by_pk("bonafideCertificate")
                            if isinstance(bonafide_reqs, list):
                                if 'bonafide' not in student_info or not isinstance(student_info['bonafide'], list):
                                    student_info['bonafide'] = []
                                
                                existing_req_ids = [b.get('req_id') for b in student_info['bonafide'] if b.get('req_id')]
                                
                                for r in bonafide_reqs:
                                    sk_val = r.get('planner-sk') or r.get('planner_sk') or ''
                                    if sk_val in ['latest_req', 'latest_cert']:
                                        continue
                                        
                                    if r.get('target_id') == val_02:
                                        if sk_val not in existing_req_ids:
                                            student_info['bonafide'].append({
                                                'req_id': sk_val,
                                                'cert_no': r.get('cert_no', ''),
                                                'date': r.get('date', r.get('dateIssued', '')),
                                                'status': r.get('status', 'Pending'),
                                                'requested_by': r.get('requested_by', ''),
                                                'generated_by': r.get('generated_by', '')
                                            })
                                            
                                # Sort by date
                                student_info['bonafide'].sort(key=lambda x: x.get('date', ''))
                        except Exception as e:
                            print("Error fetching bonafide requests:", e)

                    print("Context: ", student_info)
                    return JsonResponse({'user_info': student_info})

                else:
                    return JsonResponse({'error': 'Student not found'}, status=404)
            else:
                return JsonResponse({'error': 'Missing planner_pk or planner_sk'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def studentObjMap(dict):
    def strip_tags(s):
        # Delegate to global sanitizer
        return sanitize_str(s)

    if not dict:
        return {}
    studentObj = {
        "planner_pk": strip_tags(dict.get('planner-pk', dict.get('planner_pk', ''))),
        "planner_sk": strip_tags(dict.get('planner-sk', dict.get('planner_sk', ''))),
        "name": strip_tags(dict.get('name', '')),
        "age": strip_tags(dict.get('age', '')),
        # Return the stored code (YES/NO) so the template select can be
        # populated and selected consistently. Use 'NO' when absent.
        "free_edu": 'YES' if strip_tags(dict.get('free-edu', dict.get('free_edu', ''))) == 'YES' else 'NO',
        "status": strip_tags(dict.get('status', '')),
        "emis": strip_tags(dict.get('emis', '')),
        "mobile": strip_tags(dict.get('mobile', '')),
        "std": strip_tags(dict.get('std', '')),
        "dob": strip_tags(dict.get('dob', '')),
        "doj": strip_tags(dict.get('doj', '')),
        "dol": strip_tags(dict.get('dol', '')),
        "password": strip_tags(dict.get('password', '')),
        "fees_paid": dict.get('fees_paid', []),
        "bonafide": dict.get('bonafide', []),
        "parent_name": strip_tags(dict.get('parent_name', '')),
        "address": strip_tags(dict.get('address', '')),
        "date": strip_tags(dict.get('date', '')),
        "type": strip_tags(dict.get('type', '')),
        "amount": strip_tags(dict.get('amount', '')),
        "purpose": strip_tags(dict.get('purpose', '')),
        "amount_words": strip_tags(dict.get('amount_words', '')),
        "billed_by": strip_tags(dict.get('billed_by', '')),
        "voucher_no": strip_tags(dict.get('planner-sk', ''))  # For vouchers, voucher_no is the planner_sk
    }
    return studentObj

@csrf_exempt
def student_update(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required keys
            planner_pk = data.get('planner_pk')
            planner_sk = data.get('planner_sk')
            if not planner_pk or not planner_sk:
                return JsonResponse({'success': False, 'error': 'planner_pk and planner_sk are required'}, status=400)

            # Coerce to strings to avoid NULL being sent to DynamoDB and sanitize
            planner_pk = sanitize_str(str(planner_pk))
            planner_sk = sanitize_str(str(planner_sk))

            # Pad numeric part to 4 digits and ensure prefix is present
            if planner_pk == "Teacher":
                clean_sk = planner_sk[3:] if planner_sk.startswith("TID") else planner_sk
                planner_sk = "TID" + clean_sk.zfill(4)
            elif planner_pk == "Student":
                clean_sk = planner_sk[3:] if planner_sk.startswith("SID") else planner_sk
                planner_sk = "SID" + clean_sk.zfill(5)
            elif planner_pk == "Admin":
                clean_sk = planner_sk[3:] if planner_sk.startswith("AID") else planner_sk
                planner_sk = "AID" + clean_sk.zfill(4)

            # Server-side validation for DOB and DOJ
            dob_str = data.get('dob')
            doj_str = data.get('doj')
            
            if dob_str:
                try:
                    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    if dob_date > date.today().replace(year=date.today().year - 3):
                        return JsonResponse({'success': False, 'error': 'Person must be at least 3 years old.'}, status=400)
                    
                    if doj_str:
                        doj_date = datetime.strptime(doj_str, '%Y-%m-%d').date()
                        try:
                            min_doj = dob_date.replace(year=dob_date.year + 3)
                        except ValueError:
                            min_doj = dob_date.replace(year=dob_date.year + 3, month=3, day=1)
                        
                        if doj_date < min_doj:
                            return JsonResponse({'success': False, 'error': 'Date of Joining must be at least 3 years after Date of Birth.'}, status=400)
                except ValueError:
                    pass

            # Server-side validation for Mobile (exactly 10 digits)
            mobile_val = data.get('mobile')
            if mobile_val and not re.fullmatch(r'\d{10}', str(mobile_val)):
                return JsonResponse({'success': False, 'error': 'Mobile number must be exactly 10 digits.'}, status=400)

            existing_item = datacrud.get(planner_pk, planner_sk)
            if not existing_item:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

            # Map existing DynamoDB hyphen-keys to underscore-keys and merge
            db_data = {k.replace('-', '_'): v for k, v in existing_item.items()}
            
            # Only update fields provided in the request body to prevent data loss
            updatable_fields = ['name', 'age', 'free_edu', 'status', 'emis', 'mobile', 'std', 'dob', 'doj', 'dol', 'parent_name', 'address']
            for field in updatable_fields:
                if field in data:
                    db_data[field] = sanitize_str(data[field])
            
            # Handle updating the bill history list
            if 'fees_paid' in data:
                db_data['fees_paid'] = data['fees_paid']

            # Update in database
            response = datacrud.put(db_data)
            
            if isinstance(response, dict) and response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return JsonResponse({'success': True, 'message': 'Student data updated successfully'})
            else:
                error_msg = response.get('error', 'Database update failed')
                return JsonResponse({'success': False, 'error': error_msg}, status=500)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def change_password(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            planner_pk = sanitize_str(data.get('planner_pk'))
            planner_sk = sanitize_str(data.get('planner_sk'))
            password = sanitize_str(data.get('password'))

            if not all([planner_pk, planner_sk, password]):
                return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)

            # Fetch the existing item to preserve all other attributes
            existing_item_raw = datacrud.get(planner_pk, planner_sk)
            if not existing_item_raw:
                return JsonResponse({'success': False, 'error': 'User not found.'}, status=404)

            # Map db keys (e.g., 'planner-pk') to python-friendly keys ('planner_pk')
            update_data = {k.replace('-', '_'): v for k, v in existing_item_raw.items()}
            
            # Update the password
            update_data['password'] = make_password(password)

            # Save the entire object back to the database
            response = datacrud.put(update_data)

            if response and response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return JsonResponse({'success': True, 'message': 'Password updated successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'Database update failed'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

#Code for Teacher
@csrf_exempt 
def teacher(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    schoolInformation = models.schoolInformation
    context = {}
    context['user_info'] = {}
    context['user_info_get'] = {}
    context['profiles'] = models.profile
    context['standards'] = models.SchoolStandard
    context['terms'] = models.term
    context['statuses'] = models.Status
    context['free_edu_choices'] = models.free_edu
    context['schoolInformation'] = models.schoolInformation
    context['schoolName'] = schoolInformation.get('schoolName')
    context['vasantham'] = schoolInformation.get('vasantham')
    context['trustName'] = schoolInformation.get('trustName')
    context['trustExt'] = schoolInformation.get('trustExt')
    context['trustAddress'] = schoolInformation.get('trustAddress')
    context['nps'] = schoolInformation.get('nps')
    context['schoolAddress'] = schoolInformation.get('schoolAddress')

    # Extract first name for Billed By display and saving
    full_name = user.get('user', '') if isinstance(user, dict) else ''
    context['first_name'] = full_name.split()[0] if full_name else ''

    return render(request, "Teacher.html", context)


def teacher_fetch(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            val_01 = "Student"
            val_02 = data.get("planner_sk")
            if not val_02:
                return JsonResponse({'error': 'Student ID is required'}, status=400)

            if val_02:
                clean_sk = val_02[3:] if val_02.startswith("SID") else val_02
                val_02 = "SID" + clean_sk.zfill(5)

            if val_01 and val_02:
                responseData = datacrud.get(val_01, val_02)
                if bool(responseData):
                    student_info = studentObjMap2(responseData)
                    return JsonResponse({'user_info': student_info})
                else:
                    return JsonResponse({'error': 'Student Not Found'}, status=404)
            else:
                return JsonResponse({'error': 'Missing Student ID'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def studentObjMap2(dict):
    def strip_tags(s):
        # Delegate to global sanitizer
        return sanitize_str(s)

    if not dict:
        return {}
    studentObj = {
        # "planner_pk": strip_tags(dict.get('planner-pk', '')),
        "planner_sk": strip_tags(dict.get('planner-sk', '')),
        "name": strip_tags(dict.get('name', '')),
        # "age": strip_tags(dict.get('age', '')),
        # Return the stored code (YES/NO) so the template select can be
        # populated and selected consistently. Use 'NO' when absent.
        #"free_edu": 'YES' if strip_tags(dict.get('free-edu', '')) == 'YES' else 'NO',
        "free_edu": strip_tags(dict.get('free-edu', "N/A")),
        "status": strip_tags(dict.get('status', '')),
        # "emis": strip_tags(dict.get('emis', '')),
        "mobile": strip_tags(dict.get('mobile', '')),
        "std": strip_tags(dict.get('std', '')),
        "fees_paid": dict.get('fees_paid', []),
        "parent_name": strip_tags(dict.get('parent_name', '')),
        "address": strip_tags(dict.get('address', ''))
        # "dob": strip_tags(dict.get('dob', '')),
        # "doj": strip_tags(dict.get('doj', '')),
        # "dol": strip_tags(dict.get('dol', ''))
    }
    print("DEBUG - Mapped studentObj:", studentObj)
    return studentObj

def num_to_words(n):
    units = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    if n == 0:
        return 'Zero Only'

    def convert(n):
        if n < 20:
            return units[int(n)]
        elif n < 100:
            return tens[int(n) // 10] + ('' if n % 10 == 0 else ' ' + units[int(n) % 10])
        elif n < 1000:
            return units[int(n) // 100] + " Hundred " + ('' if n % 100 == 0 else ' and ' + convert(n % 100))
        elif n < 100000:
            return convert(int(n) // 1000) + " Thousand " + ('' if n % 1000 == 0 else ' ' + convert(n % 1000))
        elif n < 10000000:
            return convert(int(n) // 100000) + " Lakh " + ('' if n % 100000 == 0 else ' ' + convert(n % 100000))
        else:
            return convert(int(n) // 10000000) + " Crore " + ('' if n % 10000000 == 0 else ' ' + convert(n % 10000000))

    return (convert(int(n)) + " Only").strip().replace("  ", " ")

@csrf_exempt
def get_fees(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sid = data.get('sid')
            std = data.get('std')
            term = data.get('term')
            type = data.get('student_type')
            sk = "Latest"
            pk = "Fees"+ std

            # Fetch Bill Number
            bill_data = datacrud.get('bill', 'latest')
            bill_no = 1
            if bill_data and 'num' in bill_data:
                try:
                    bill_no = int(bill_data['num']) + 1
                except ValueError:
                    pass

            # Logic to fetch actual fees from your database goes here
            responseData = datacrud.get(pk,sk)

            # Filter term-specific keys from responseData before mapping names
            # Assuming DB keys are 'term1', 'term2', 'term3'
            all_terms = ["term1", "term2", "term3"]
            if term in all_terms:
                for t in all_terms:
                    if t != term:
                        responseData.pop(t, None)
            if type == "OLD":
                responseData.pop("regisFee", None)
                responseData.pop("admisionFee", None)


            # Map internal DB keys to display names and filter metadata
            fee_name_map = models.feeNames
            fees_display = {}
            total_amount = 0
            
            for k, v in responseData.items():
                if k in ['planner-pk', 'planner-sk']:
                    continue
                
                try:
                    amount = float(v)
                except (ValueError, TypeError):
                    amount = 0.0
                
                total_amount += amount
                display_name = fee_name_map.get(k, k)
                fees_display[display_name] = amount
            
            return JsonResponse({
                'success': True,
                'sid': sid,
                'std': std,
                'fees': fees_display,
                'total_amount': total_amount,
                'amount_in_words': num_to_words(total_amount),
                'bill_no': "VS" + str(bill_no).zfill(5)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def voucher_save(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED":
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voucher_no = data.get('voucher_no')
            
            # Sequential Numbering Logic for new vouchers
            if not voucher_no:
                res = datacrud.get('vouchers', 'latest')
                num = int(res.get('num', 0)) + 1
                voucher_no = "VOU" + str(num).zfill(5)
                
                # Update the counter
                bill_res = datacrud.put_bill({
                    'planner_pk': 'vouchers',
                    'planner_sk': 'latest',
                    'num': num
                })
                if bill_res and 'error' in bill_res:
                    return JsonResponse({'success': False, 'error': f"Counter update failed: {bill_res['error']}"}, status=500)
            
            # Preserving existing status if it's an update to prevent overwriting approvals
            status_to_save = 'Pending'
            existing = datacrud.get('vouchers', voucher_no)
            if existing and existing.get('status'):
                status_to_save = existing.get('status')

            save_data = {
                'date': data.get('date'),
                'type': data.get('type'), # Payment or Receipt
                'name': sanitize_str(data.get('name')),
                'mobile': sanitize_str(data.get('mobile')),
                'amount': str(data.get('amount')),
                'purpose': sanitize_str(data.get('purpose')),
                'billed_by': user.get('user', 'Teacher'),
                'status': status_to_save,
                'amount_words': data.get('amount_words')
            }
            
            # Using generic put_fee for flexibility (pk='vouchers', sk=voucher_no)
            fee_res = datacrud.put_fee('vouchers', voucher_no, save_data)
            if fee_res and 'error' in fee_res:
                return JsonResponse({'success': False, 'error': f"Database save failed: {fee_res['error']}"}, status=500)
            
            return JsonResponse({
                'success': True, 
                'message': 'Voucher saved successfully', 
                'voucher_no': voucher_no
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_pending_vouchers(request):
    user = request.session.get('user')
    if not user or (isinstance(user, dict) and user.get('pk') != 'Admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # Fetch Vouchers
        voucher_results = datacrud.scan_by_pk("vouchers")

        pending = []
        
        # Process Vouchers
        if isinstance(voucher_results, list):
            for v in voucher_results:
                status_val = str(v.get('status', '')).strip().lower()
                sk_val = v.get('planner-sk') or v.get('planner_sk') or ''
                if (status_val == 'pending' or status_val.startswith('in progress')) and sk_val != 'latest':
                    item = studentObjMap(v)
                    item['approval_type'] = 'Voucher'
                    pending.append(item)

        # Process Bonafide Requests from bonafideCertificate table
        bonafide_results = datacrud.scan_by_pk("bonafideCertificate")
        if isinstance(bonafide_results, list):
            for r in bonafide_results:
                status_val = str(r.get('status', '')).strip().lower()
                sk_val = r.get('planner-sk') or r.get('planner_sk') or ''
                if sk_val not in ['latest_req', 'latest_cert'] and (status_val in ['pending', 'saved'] or status_val.startswith('in progress')):
                    item = studentObjMap(r)
                    item['planner_sk'] = sk_val
                    item['approval_type'] = 'Bonafide'
                    item['purpose'] = r.get('purpose', '')
                    item['target_id'] = r.get('target_id', '')
                    item['profile'] = r.get('profile', '')
                    item['requested_by'] = r.get('requested_by', '')
                    item['name'] = r.get('name', '')
                    item['date'] = r.get('date', r.get('dateIssued', ''))
                    item['status'] = r.get('status', '')
                    item['cert_no'] = r.get('cert_no', '')
                    item['cert_num_int'] = r.get('cert_num_int', '')
                    pending.append(item)

        return JsonResponse({'success': True, 'vouchers': pending})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def approve_voucher(request):
    user = request.session.get('user')
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', '')
            # Strict Admin check unless the action is just 'Signed' (Teacher side)
            if action.upper() != 'SIGNED' and (isinstance(user, dict) and user.get('pk') != 'Admin'):
                return JsonResponse({'error': 'Unauthorized'}, status=401)

            item_id = data.get('item_id') or data.get('voucher_no')
            item_type = data.get('type', 'Voucher')
            admin_name = user.get('user', 'Admin')
            admin_id = user.get('sk', 'Admin')

            action_upper = action.upper()
            if action_upper == 'APPROVED':
                status_to_save = f"APPROVED ({admin_name})"
            elif action_upper == 'COMPLETED':
                status_to_save = f"APPROVED ({admin_name})"
            elif action_upper == 'IN PROGRESS':
                status_to_save = f"In Progress ({admin_name})"
            else:
                status_to_save = action

            if item_type == 'Bonafide':
                pk = 'bonafideCertificate'
                req_data = datacrud.get(pk, item_id)
                if not req_data:
                    return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
                    
                response = datacrud.update_status(pk, item_id, status_to_save, admin_name)
                if isinstance(response, dict) and 'error' in response:
                    return JsonResponse({'success': False, 'error': response['error']}, status=500)
                    
                if action_upper == 'SIGNED':
                    profile = req_data.get('profile')
                    target_id = req_data.get('target_id')
                    if profile and target_id:
                        cert_data = req_data.copy()
                        cert_data['status'] = status_to_save
                        datacrud.update_bonafide(profile, target_id, cert_data)
            else:
                pk = 'vouchers'
                response = datacrud.update_status(pk, item_id, status_to_save, admin_name)
                if isinstance(response, dict) and 'error' in response:
                    return JsonResponse({'success': False, 'error': response['error']}, status=500)

            return JsonResponse({'success': True, 'message': f'{item_type} {action} successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
def get_vouchers_by_mobile(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED":
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            
            if not mobile:
                return JsonResponse({'success': False, 'error': 'Mobile number is required'}, status=400)
            
            # Scan for all vouchers with this mobile number
            vouchers = datacrud.scan_by_mobile("vouchers", mobile)
            
            if isinstance(vouchers, list):
                # Convert to the expected format and sort by date (newest first)
                voucher_list = []
                for v in vouchers:
                    if v.get('planner-sk') != 'latest':  # Skip the counter entry
                        voucher_info = studentObjMap(v)
                        voucher_list.append(voucher_info)
                
                # Sort by date (newest first)
                voucher_list.sort(key=lambda x: x.get('date', ''), reverse=True)
                
                return JsonResponse({
                    'success': True, 
                    'vouchers': voucher_list,
                    'count': len(voucher_list)
                })
            else:
                return JsonResponse({'success': False, 'error': 'Failed to fetch vouchers'}, status=500)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# In views.py
@csrf_exempt
def send_whatsapp(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            message = data.get('message')

            if not mobile or not message:
                return JsonResponse({'success': False, 'error': 'Mobile and message required.'}, status=400)

            # URL encode the message to handle spaces and special characters
            encoded_message = quote(message)
            # Construct the WhatsApp API URL (Using +91 for India context)
            whatsapp_url = f"https://wa.me/91{mobile}?text={encoded_message}"

            return JsonResponse({'success': True, 'whatsapp_url': whatsapp_url})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def save_fees(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return redirect('/login/')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received fee payment data:", data)
            # Extract necessary fields from the request
            sid = data.get('sid')
            std = data.get('std')
            term = data.get('term')
            amount_paid = data.get('amount_paid')
            payment_date = data.get('payment_date')
            billed_by = data.get('billed_by')
            bill_no_str = data.get('bill_no')
            payment_type = data.get('payment_type')
            fee_particulars = data.get('fee_particulars')

            # Validate required fields (check amount_paid for None, as 0 is valid)
            if not all([sid, std, term, payment_date, billed_by, bill_no_str, payment_type]) or amount_paid is None:
                return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)

            # Convert amount_paid to string to prevent boto3 float error
            data['amount_paid'] = str(amount_paid)

            datacrud.update(data)
            # Here you would implement logic to save the payment details to your database
            # For demonstration, we'll just print the details and return a success response
            print(f"Saving payment for SID: {sid}, STD: {std}, TERM: {term}, Amount Paid: {amount_paid}, Payment Date: {payment_date}, Billed By: {billed_by}, Bill Number: {bill_no_str}")

            # Update Bill Number Counter in DB
            if bill_no_str:
                try:
                    # Extract number from "VS00001" format
                    current_num = int(re.sub(r'\D', '', bill_no_str))
                    print("BILL NUM: ", current_num)
                    datacrud.put_bill({
                        'planner_pk': 'bill',
                        'planner_sk': 'latest',
                        'num': current_num
                    })
                except (ValueError, TypeError):
                    pass

            return JsonResponse({'success': True, 'message': 'Payment details saved successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_fee_details(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            std = data.get('std')
            if not std:
                return JsonResponse({'success': False, 'error': 'Standard is required'}, status=400)
            
            pk = "Fees" + std
            sk = "Latest"
            response_data = datacrud.get(pk, sk)
            
            if response_data:
                # Filter out internal keys
                filtered_data = {}
                for k, v in response_data.items():
                    if k not in ['planner-pk', 'planner-sk']:
                        try:
                            # Convert Decimal to float/int for JSON serialization
                            val = float(v)
                            filtered_data[k] = int(val) if val.is_integer() else val
                        except (ValueError, TypeError):
                            filtered_data[k] = str(v)
                return JsonResponse({'success': True, 'data': filtered_data})
            else:
                return JsonResponse({'success': False, 'error': 'No details found for this standard'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def update_fee_details(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            std = data.get('std')
            fees = data.get('fees')
            
            if not std or not fees:
                return JsonResponse({'success': False, 'error': 'Standard and fees data are required'}, status=400)
            
            pk = "Fees" + std
            sk = "Latest"
            response = datacrud.put_fee(pk, sk, fees)
            return JsonResponse({'success': True, 'message': 'Fee details updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_all_fee_details(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        standards = models.SchoolStandard
        data_list = []
        all_columns = set()

        for s in standards:
            std_val = s[0]
            pk = "Fees" + std_val
            sk = "Latest"
            item = datacrud.get(pk, sk)
            if item and isinstance(item, dict):
                row = {'Standard': std_val}
                for k, v in item.items():
                    if k not in ['planner-pk', 'planner-sk']:
                        # Convert Decimal to float/int to ensure JSON serialization works
                        try:
                            val = float(v)
                            row[k] = int(val) if val.is_integer() else val
                        except (ValueError, TypeError):
                            row[k] = str(v)
                        all_columns.add(k)
                data_list.append(row)
        
        return JsonResponse({'success': True, 'data': data_list, 'columns': sorted(list(all_columns))})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
# Create your views here.

@csrf_exempt
def save_bonafide(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED" or (isinstance(user, dict) and (user.get('user') == "ACCESS DENIED" or not user.get('user'))):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = data.get('profile')
            student_id = data.get('id')
            req_id = data.get('req_id')
            
            if not profile or not student_id or not req_id:
                return JsonResponse({'success': False, 'error': 'Profile, ID, and Request ID are required'}, status=400)
            
            # Ensure status is recorded in the appended DB item
            data['status'] = 'Saved'

            # Update existing request
            req_data = datacrud.get('bonafideCertificate', req_id)
            if req_data:
                for k, v in data.items():
                    req_data[k] = v
                resp = datacrud.put_fee('bonafideCertificate', req_id, req_data)
                if isinstance(resp, dict) and 'error' in resp:
                    return JsonResponse({'success': False, 'error': resp['error']}, status=500)
            else:
                return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
            
            # Update Bonafide Counter
            cert_num_int = data.get('cert_num_int')
            if cert_num_int:
                current_latest = datacrud.get('bonafideCertificate', 'latest_cert')
                current_num = int(current_latest.get('num', 0)) if current_latest else 0
                if int(cert_num_int) > current_num:
                    datacrud.put_bill({
                        'planner_pk': 'bonafideCertificate',
                        'planner_sk': 'latest_cert',
                        'num': int(cert_num_int)
                    })

            return JsonResponse({'success': True, 'message': 'Bonafide certificate saved successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def enquiry_save(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enq_id = data.get('enq_id')
            
            if not enq_id:
                # Generate new ID (ENQ00001 format) using the counter logic
                res = datacrud.get('enquiry', 'latest')
                num = int(res.get('num', 0)) + 1
                enq_id = "ENQ" + str(num).zfill(5)
                # Update counter
                datacrud.put_bill({
                    'planner_pk': 'enquiry',
                    'planner_sk': 'latest',
                    'num': num
                })
            
            save_data = {
                'name': sanitize_str(data.get('name')),
                'parent_name': sanitize_str(data.get('parent_name')),
                'std': sanitize_str(data.get('std')),
                'mobile': sanitize_str(data.get('mobile')),
                'address': sanitize_str(data.get('address')),
                'date': data.get('date')
            }
            
            datacrud.put_fee('Enquiry', enq_id, save_data)
            return JsonResponse({'success': True, 'message': 'Enquiry saved successfully', 'enq_id': enq_id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def enquiry_delete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enq_id = data.get('enq_id')
            if not enq_id:
                return JsonResponse({'success': False, 'error': 'ID is required'}, status=400)
            
            response = datacrud.delete('Enquiry', enq_id)
            if 'error' in response:
                return JsonResponse({'success': False, 'error': response['error']}, status=500)
            return JsonResponse({'success': True, 'message': 'Enquiry deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def bonafide_request_save(request):
    user = request.session.get('user')
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Generate Sequential Request ID
            res = datacrud.get('bonafideCertificate', 'latest_req')
            num = int(res.get('num', 0)) + 1
            req_id = "BREQ" + str(num).zfill(6)
            
            # Update the counter in database
            datacrud.put_bill({
                'planner_pk': 'bonafideCertificate',
                'planner_sk': 'latest_req',
                'num': num
            })
            
            # Fetch the actual name from the target record to store with the request
            target_pk = data.get('profile')
            target_sk = data.get('id') or ""
            
            # Normalize ID for lookup to ensure name retrieval (e.g. "1" -> "SID00001")
            if target_pk == "Teacher":
                clean_sk = target_sk[3:] if target_sk.startswith("TID") else target_sk
                target_sk = "TID" + clean_sk.zfill(4)
            elif target_pk == "Student":
                clean_sk = target_sk[3:] if target_sk.startswith("SID") else target_sk
                target_sk = "SID" + clean_sk.zfill(5)

            target_name = 'N/A'
            if target_pk and target_sk:
                target_rec = datacrud.get(target_pk, target_sk)
                if target_rec:
                    target_name = target_rec.get('name', 'N/A')

            save_data = {
                'req_id': req_id,
                'profile': target_pk,
                'target_id': target_sk,
                'name': target_name,
                'purpose': sanitize_str(data.get('purpose')),
                'mobile': sanitize_str(data.get('mobile')),
                'status': 'Pending',
                'requested_by': user.get('user'),
                'date': date.today().strftime('%Y-%m-%d')
            }
            
            resp = datacrud.put_fee('bonafideCertificate', req_id, save_data)
            if isinstance(resp, dict) and 'error' in resp:
                 return JsonResponse({'success': False, 'error': resp['error']}, status=500)
            return JsonResponse({'success': True, 'message': 'Bonafide request sent to admin', 'req_id': req_id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_my_requests(request):
    user = request.session.get('user')
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        username = user.get('user')
        
        my_requests = []
        bonafide_results = datacrud.scan_by_pk("bonafideCertificate")
        if isinstance(bonafide_results, list):
            for r in bonafide_results:
                status_val = str(r.get('status', '')).strip().lower()
                sk_val = r.get('planner-sk') or r.get('planner_sk') or ''
                req_by = r.get('requested_by', '')
                
                if sk_val not in ['latest_req', 'latest_cert'] and (status_val in ['pending', 'saved'] or status_val.startswith('in progress')) and req_by == username:
                    item = studentObjMap(r)
                    item['req_id'] = sk_val
                    item['target_id'] = r.get('target_id', '')
                    item['profile'] = r.get('profile', '')
                    item['name'] = r.get('name', '')
                    item['date'] = r.get('date', r.get('dateIssued', ''))
                    item['status'] = r.get('status', '')
                    item['purpose'] = r.get('purpose', '')
                    my_requests.append(item)
                    
        return JsonResponse({'success': True, 'requests': my_requests})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def setup_mfa(request):
    user = request.session.get('user')
    if not user or user == "ACCESS DENIED":
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pk = sanitize_str(data.get('planner_pk'))
            sk = sanitize_str(data.get('planner_sk'))
            
            if pk == 'Student':
                return JsonResponse({'success': False, 'error': 'MFA is currently only supported for Staff/Admin profiles.'}, status=400)

            action = data.get('action')

            # Step 3: Remove MFA
            if action == 'remove':
                existing_rec = datacrud.get(pk, sk)
                if not existing_rec:
                    return JsonResponse({'success': False, 'error': 'User not found.'}, status=404)
                
                update_data = {k.replace('-', '_'): v for k, v in existing_rec.items()}
                update_data['totp_secret'] = ''
                datacrud.put(update_data)
                return JsonResponse({'success': True, 'message': 'MFA has been removed successfully.'})

            # Step 4: Verify Existing MFA (Testing)
            if action == 'verify':
                otp_token = data.get('otp_token')
                existing_rec = datacrud.get(pk, sk)
                if not existing_rec or not existing_rec.get('totp_secret'):
                    return JsonResponse({'success': False, 'error': 'MFA is not enabled for this user.'})
                
                totp = pyotp.TOTP(existing_rec.get('totp_secret'))
                if totp.verify(otp_token):
                    return JsonResponse({'success': True, 'message': 'MFA verification successful! Your app is synced.'})
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid OTP code.'})

            otp_token = data.get('otp_token')
            temp_secret = data.get('secret')

            # Step 2: Verification and Saving
            if otp_token and temp_secret:
                totp = pyotp.TOTP(temp_secret)
                if totp.verify(otp_token):
                    existing_rec = datacrud.get(pk, sk)
                    if not existing_rec:
                        return JsonResponse({'success': False, 'error': 'User not found.'}, status=404)
                    
                    update_data = {k.replace('-', '_'): v for k, v in existing_rec.items()}
                    update_data['totp_secret'] = temp_secret
                    datacrud.put(update_data)
                    return JsonResponse({'success': True, 'message': 'MFA verified and enabled successfully.'})
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid OTP code. Please try again.'})

            # Step 1: Initial Generation
            new_secret = pyotp.random_base32()
            totp = pyotp.TOTP(new_secret)
            issuer = models.schoolInformation.get('schoolName', 'Vasantham School')
            uri = totp.provisioning_uri(name=sk, issuer_name=issuer)

            return JsonResponse({'success': True, 'secret': new_secret, 'uri': uri})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
