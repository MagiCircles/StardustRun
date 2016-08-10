from web.utils import globalContext as web_globalContext

def globalContext(request):
    context = web_globalContext(request)
    return context
