def salebox(request):
    return {
        'basket': request.session['saleboxbasket'],
        'user': request.user
    }
