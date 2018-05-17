import os
from django import template
from django.conf import settings
register = template.Library()

@register.filter
def filename(value):
    try:
        if value and os.path.basename(value.file.name): # if no file is found, exception will be raised and value set to None
            value = str(value)
            c = '/'
            psts_list = [pos+1 for pos, char in enumerate(value) if char == c]
            if psts_list:
                last_pst = psts_list[-1]
                return value[last_pst:]
            else:
                return value
    except IOError:
        return None


@register.simple_tag()
def check_file(filename):
    if filename is not None:
        return True
    else:
        return False
        # if path:
        #     return True #os.path.basename(value.file.name)

        #return False
    #
    # file_path = os.path.join(settings.MEDIA_ROOT, path)
    # if os.path.exists(file_path):
    #     return True
    # else:
    #     return False
