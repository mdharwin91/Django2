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
            
            if not profile or not student_id:
                return JsonResponse({'success': False, 'error': 'Profile and ID are required'}, status=400)
            
            # Save to Student/Teacher Record
            resp = datacrud.update_bonafide(profile, student_id, data)
            if isinstance(resp, dict) and 'error' in resp:
                 return JsonResponse({'success': False, 'error': resp['error']}, status=500)
            
            # Update BonafideRequests Counter and save record
            cert_num_int = data.get('cert_num_int')
            if cert_num_int:
                # Update the counter in BonafideRequests
                datacrud.put_bill({
                    'planner_pk': 'BonafideRequests',
                    'planner_sk': 'latest',
                    'num': int(cert_num_int)
                })
                
                # Save to BonafideRequests with the incremented number as SK
                req_id = "REQ" + str(int(cert_num_int)).zfill(5)
                bonafide_data = {
                    'profile': profile,
                    'target_id': student_id,
                    'name': data.get('name', 'N/A'),
                    'cert_no': data.get('cert_no'),
                    'date': data.get('date'),
                    'emis': data.get('emis'),
                    'std': data.get('std'),
                    'doj': data.get('doj'),
                    'dol': data.get('dol'),
                    'status': 'Signed',
                    'generated_by': user.get('user'),
                    'generated_date': date.today().strftime('%Y-%m-%d')
                }
                datacrud.put_fee('BonafideRequests', req_id, bonafide_data)

            return JsonResponse({'success': True, 'message': 'Bonafide certificate saved successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
