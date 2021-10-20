#
# AUTHOR : LAWRENCE GANDHAR
# Project For Theo - (Greece)
# Project Date : 28th March 2021
#


from django.contrib.auth.decorators import user_passes_test

# *************************************************************************************
# ADMIN ACCESS CHECK
# *************************************************************************************

def admin_required(view_func=None, login_url='/page_403/'):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
