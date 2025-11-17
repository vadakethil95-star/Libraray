from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Book, User,Cart



def index(request):

    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(Q(name__icontains=query) | Q(author__icontains=query))
    else:
        books = Book.objects.all()
    return render(request, 'index.html', {'books': books, 'query': query})


def signup_page(request):
    message = ""
    success = ""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            message = "Passwords do not match!"
        elif User.objects.filter(username=username).exists():
            message = "Username already taken!"
        elif User.objects.filter(email=email).exists():
            message = "Email already registered!"
        else:
            User.objects.create(username=username, email=email, password=password)
            success = "Registration successful! You can now login."

    return render(request, 'signup.html', {'message': message, 'success': success})


def login_page(request):

    message = ""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

      
        if username == 'admin' and password == 'admin123':
            request.session['is_admin'] = True
            messages.success(request, "Welcome Admin")
            return redirect('admin_index')

        user = User.objects.filter(username=username, password=password).first()
        if user:
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_admin'] = False
            messages.success(request, f"Welcome {user.username}!")
            return redirect('index')
        else:
            message = "Invalid username or password!"

    return render(request, 'login.html', {'message': message})


def logout_page(request):
    request.session.flush()
    return redirect('login')


def admin_index(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    books = Book.objects.all().order_by('-id')
    return render(request, 'admin_index.html', {'books': books})


def upload_book(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('book_name', '').strip()
        author = request.POST.get('author_name', '').strip()
        price = request.POST.get('price', '0').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('book_image')
        Book.objects.create(
            name=name,
            author=author,
            price=price or 0,
            description=description,
            image=image
        )
        messages.success(request, "Book uploaded successfully!")
        return redirect('admin_index')

    return render(request, 'upload_book.html')


def edit_book(request, book_id):
    if not request.session.get('is_admin'):
        return redirect('login')

    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.name = request.POST.get('book_name', '').strip()
        book.author = request.POST.get('author_name', '').strip()
        book.price = request.POST.get('price', '0').strip()
        book.description = request.POST.get('description', '').strip()
        if request.FILES.get('book_image'):
            book.image = request.FILES['book_image']
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect('admin_index')

    return render(request, 'edit_book.html', {'book': book})


def delete_book(request, book_id):
    if not request.session.get('is_admin'):
        return redirect('login')

    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('admin_index')

def library_view(request):
    query = request.GET.get("q", "")
    if query:
        books = Book.objects.filter(
            Q(name__icontains=query) | Q(author__icontains=query)
        )
    else:
        books = Book.objects.all()
    return render(request, "library.html", {"books": books, "query": query})



def add_to_cart(request, book_id):
    user = User.objects.first()
    book = get_object_or_404(Book, id=book_id)

    cart_item, created = Cart.objects.get_or_create(user=user, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"'{book.name}' added to cart!")
    return redirect("index")


def view_cart(request):
    user = User.objects.first()
    cart_items = Cart.objects.filter(user=user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, "cart.html", {"cart_items": cart_items, "total": total})


def delete_from_cart(request, cart_id):
    user = User.objects.first()
    cart_item = get_object_or_404(Cart, id=cart_id, user=user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("view_cart")