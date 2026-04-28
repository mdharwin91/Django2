def user_context(request):
    return {'user': request.session.get('user', '')}
