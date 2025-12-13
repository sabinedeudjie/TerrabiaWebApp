"""
Custom CSRF error handling
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden


def csrf_failure_view(request, reason=""):
    """
    Custom view to handle CSRF failures.
    Redirects user back with a helpful message.
    """
    messages.error(
        request,
        "Your session may have expired. Please refresh the page and try again."
    )
    # Try to redirect to the previous page or landing page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('accounts:landing')



