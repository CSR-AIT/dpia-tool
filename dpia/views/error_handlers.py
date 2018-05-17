from dpia.modules import *

@login_required
def handler404(request):
    response = render(request, 'not_found/404.html')
    response.status_code = 404
    return response

# @login_required
# def handler500(request):
#     response = render_to_response(request, 'not_found/404.html')
#     response.status_code = 500
#     return response
