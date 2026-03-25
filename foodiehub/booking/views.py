from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Restaurant, Table, Booking


# 🏠 HOME PAGE
def home(request):
    query = request.GET.get('q')

    if query:
        restaurants = Restaurant.objects.filter(name__icontains=query)
    else:
        restaurants = Restaurant.objects.all()

    return render(request, 'home.html', {'restaurants': restaurants})

# 🔐 LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔥 FORCE REDIRECT AFTER LOGIN
            return redirect('/')  

        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')


# 📝 SIGNUP
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        User.objects.create_user(username=username, password=password)

        return redirect('/login/')

    return render(request, 'signup.html')


# 🚪 LOGOUT
def logout_view(request):
    logout(request)

    # 🔥 FORCE REDIRECT AFTER LOGOUT
    return redirect('/')


# 🍽 BOOK TABLE (WITH DOUBLE BOOKING PREVENTION)
def book_table(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    tables = Table.objects.all()

    if request.method == 'POST':
        table_id = request.POST.get('table')
        date = request.POST.get('date')
        time = request.POST.get('time')

        if table_id and date and time:
            table = Table.objects.get(id=table_id)

            # 🔥 CHECK DOUBLE BOOKING
            existing = Booking.objects.filter(
                table=table,
                date=date,
                time=time
            )

            if existing.exists():
                return render(request, 'booking.html', {
                    'tables': tables,
                    'error': '❌ This table is already booked for that time!'
                })

            # ✅ SAVE BOOKING
            Booking.objects.create(
                user=request.user,
                table=table,
                date=date,
                time=time
            )

            return render(request, 'booking.html', {
                'tables': tables,
                'success': '✅ Booking successful!'
            })

    return render(request, 'booking.html', {'tables': tables})


# 📜 BOOKING HISTORY
def booking_history(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    bookings = Booking.objects.filter(user=request.user)

    return render(request, 'history.html', {'bookings': bookings})