"""
Messaging app views - Conversations and Messages
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from .models import MessageThread, Message
from accounts.decorators import farmer_required, agency_required
from accounts.models import DeliveryAgency, FarmerProfile


@farmer_required
def farmer_messages(request):
    """List all message threads for a farmer."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    # Get all threads where farmer is a participant
    threads = MessageThread.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-updated_at')
    
    # Get thread details with last message and unread count
    thread_list = []
    for thread in threads:
        last_message = thread.messages.last()
        unread_count = thread.messages.filter(is_read=False).exclude(sender=request.user).count()
        other_participant = thread.get_other_participant(request.user)
        
        thread_list.append({
            'thread': thread,
            'last_message': last_message,
            'unread_count': unread_count,
            'other_participant': other_participant,
        })
    
    context = {
        'threads': thread_list,
    }
    
    return render(request, 'messaging/farmer_messages.html', context)


@farmer_required
def farmer_message_thread(request, thread_id):
    """View a specific message thread for a farmer."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    thread = get_object_or_404(MessageThread, id=thread_id, participants=request.user)
    
    # Mark messages as read
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages in the thread
    message_list = thread.messages.all()
    
    # Get other participant
    other_participant = thread.get_other_participant(request.user)
    
    # Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )
            thread.save()  # Update updated_at
            messages.success(request, "Message sent!")
            return redirect('messaging:farmer_thread', thread_id=thread_id)
        else:
            messages.error(request, "Message cannot be empty.")
    
    context = {
        'thread': thread,
        'messages': message_list,
        'other_participant': other_participant,
    }
    
    return render(request, 'messaging/farmer_thread.html', context)


@farmer_required
def farmer_start_conversation(request, agency_id):
    """Start a new conversation with a delivery agency."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    agency = get_object_or_404(DeliveryAgency, id=agency_id)
    
    # Check if thread already exists between farmer and agency
    # Get all threads where farmer is a participant
    farmer_threads = MessageThread.objects.filter(participants=request.user)
    # Check if any of these threads also has the agency as participant
    existing_thread = None
    for thread in farmer_threads:
        if agency.account in thread.participants.all():
            existing_thread = thread
            break
    
    if existing_thread:
        return redirect('messaging:farmer_thread', thread_id=existing_thread.id)
    
    # Get order ID from query parameter if provided
    order_id = request.GET.get('order')
    order = None
    if order_id:
        from orders.models import Order
        try:
            order = Order.objects.get(id=order_id, items__farmer=farmer)
        except Order.DoesNotExist:
            pass
    
    # Create new thread
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        content = request.POST.get('content', '').strip()
        order_id_from_form = request.POST.get('order_id')
        
        if content:
            # Get order if provided
            order_for_thread = None
            if order_id_from_form:
                from orders.models import Order
                try:
                    order_for_thread = Order.objects.get(id=order_id_from_form, items__farmer=farmer)
                except Order.DoesNotExist:
                    pass
            
            # Create subject based on order if available
            if not subject and order_for_thread:
                subject = f"Delivery for Order {order_for_thread.code}"
            elif not subject:
                subject = f"Conversation with {agency.agency_name}"
            
            thread = MessageThread.objects.create(
                subject=subject,
                order=order_for_thread
            )
            thread.participants.add(request.user, agency.account)
            
            # Create first message
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )
            
            messages.success(request, "Conversation started!")
            return redirect('messaging:farmer_thread', thread_id=thread.id)
        else:
            messages.error(request, "Message cannot be empty.")
    
    context = {
        'agency': agency,
        'order': order,
    }
    
    return render(request, 'messaging/farmer_start_conversation.html', context)


@agency_required
def agency_messages(request):
    """List all message threads for a delivery agency."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    # Get all threads where agency is a participant
    threads = MessageThread.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-updated_at')
    
    # Get thread details with last message and unread count
    thread_list = []
    for thread in threads:
        last_message = thread.messages.last()
        unread_count = thread.messages.filter(is_read=False).exclude(sender=request.user).count()
        other_participant = thread.get_other_participant(request.user)
        
        thread_list.append({
            'thread': thread,
            'last_message': last_message,
            'unread_count': unread_count,
            'other_participant': other_participant,
        })
    
    context = {
        'threads': thread_list,
    }
    
    return render(request, 'messaging/agency_messages.html', context)


@farmer_required
def farmer_agencies(request):
    """List all available delivery agencies for farmers to contact."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    from accounts.models import DeliveryAgency
    from accounts.location_models import CoverageArea
    
    # Get all verified agencies
    agencies = DeliveryAgency.objects.filter(status=DeliveryAgency.STATUS_VERIFIED).order_by('agency_name')
    
    # Group by coverage area
    agencies_by_area = {}
    for agency in agencies:
        if agency.coverage_area:
            area_name = agency.coverage_area.name
            if area_name not in agencies_by_area:
                agencies_by_area[area_name] = []
            agencies_by_area[area_name].append(agency)
    
    # Get all coverage areas for filter
    coverage_areas = CoverageArea.objects.all().order_by('name')
    
    # Filter by coverage area if provided
    selected_area = request.GET.get('area', '')
    if selected_area:
        agencies = agencies.filter(coverage_area_id=selected_area)
        agencies_by_area = {k: v for k, v in agencies_by_area.items() if any(a.coverage_area_id == int(selected_area) for a in v)}
    
    context = {
        'agencies': agencies,
        'agencies_by_area': agencies_by_area,
        'coverage_areas': coverage_areas,
        'selected_area': selected_area,
    }
    
    return render(request, 'messaging/farmer_agencies.html', context)


@agency_required
def agency_message_thread(request, thread_id):
    """View a specific message thread for a delivery agency."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    thread = get_object_or_404(MessageThread, id=thread_id, participants=request.user)
    
    # Mark messages as read
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages in the thread
    message_list = thread.messages.all()
    
    # Get other participant
    other_participant = thread.get_other_participant(request.user)
    
    # Handle sending a new message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )
            thread.save()  # Update updated_at
            messages.success(request, "Message sent!")
            return redirect('messaging:agency_thread', thread_id=thread_id)
        else:
            messages.error(request, "Message cannot be empty.")
    
    context = {
        'thread': thread,
        'messages': message_list,
        'other_participant': other_participant,
    }
    
    return render(request, 'messaging/agency_thread.html', context)
