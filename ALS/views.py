import os
import random
import json
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Book, BorrowRecord
from django.conf import settings
from .forms import ProfileForm, UserEmailForm
from .models import Profile
from .models import Book, BorrowRecord
import os, json
from django.conf import settings
from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from ALS.models import User

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def manage_books(request):
    return render(request, "ALS/manage_books.html")


@login_required
def student_dashboard_view(request):
    return render(request, "ALS/dashboard.html")


# Make sure the path is correct
BOOKS_FILE = os.path.join(settings.BASE_DIR, "ALS", "books.json")


def manage_students(request):
    students = User.objects.filter(is_staff=False, is_superuser=False)
    return render(request, "ALS/manage_students.html", {"students": students})


QA_DATABASE = {
    "how many books": "There are 50 total books in the library.",
    "total books": "We currently have 50 total books.",
    "available books": "There are 48 available books ready for borrowing.",
    "borrowed books": "Right now, 2 books are borrowed.",
    "library hours": "The library is open from 8 AM to 5 PM, Monday to Friday.",
    "return book": "You can return a book in the Returned Books page.",
    "borrow book": "Go to the Borrow Book page and select a book.",
    "rules": "Borrowing rules: maximum of 7 days, one book per student.",
    "help": "You can ask about books, schedule, borrowing, returning, and rules.",
    "hello": "Hey there! How's your day going? 😊",
    "hi": "Hi! I'm your library buddy 🤓",
    "how are you": "I'm feeling like a million books stacked perfectly! 😎 How about you?",
    "joke": "Why did the book go to the doctor? Because it had too many 'chapters'! 😂",
    "thank you": "You're welcome! Happy reading! 📚",
    "bye": "Goodbye! Don't forget to return your books on time 😉",
}


def nlp_match(message):
    msg = message.lower().split()
    best_score = 0
    best_answer = "Hmm... I’m not sure about that. 😅"

    for question, answer in QA_DATABASE.items():
        tokens = question.split()
        score = len(set(tokens) & set(msg))
        for word in msg:
            if word in question:
                score += 1
        if score > best_score:
            best_score = score
            # Randomly add a friendly emoji or phrase
            emojis = ["😊", "😎", "📚", "😂", "😉"]
            best_answer = f"{answer} {random.choice(emojis)}"

    return best_answer


def login_view(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(request, username=id_number, password=password)

        if user is not None:
            # Check role
            if role == "admin" and user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username} (Admin)!")
                return redirect("admin_dashboard")
            elif role == "student" and not user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("student_dashboard")
                messages.error(request, "Incorrect role selected for this account.")
        else:
            messages.error(request, "Invalid ID Number or password.")

    return render(request, "ALS/login.html")


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, "ALS/admin_dashboard.html")


def register_view(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number")
        full_name = request.POST.get("username")  # <-- NEW
        email = request.POST.get("email")  # <-- NEW
        password = request.POST.get("password")

        if User.objects.filter(username=id_number).exists():
            messages.error(request, "ID Number already registered.")
        else:
            # Create user with ID as username, full name, and email
            User.objects.create_user(
                username=id_number, first_name=full_name, email=email, password=password
            )
            messages.success(request, "Account created successfully!")
            return redirect("login")

    return render(request, "ALS/signup.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


def library_home(request):
    return render(request, "ALS/library.html")


BOOKS_JSON = os.path.join(os.path.dirname(__file__), "books.json")


def load_books():
    with open(BOOKS_JSON, "r") as f:
        return json.load(f)


def save_books(books):
    with open(BOOKS_JSON, "w") as f:
        json.dump(books, f, indent=2)


@csrf_exempt
@login_required
def add_book(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title")
        category = data.get("category")
        otp_code = data.get("otp_code")
        img = data.get("img")

        if not all([title, category, otp_code, img]):
            return JsonResponse({"success": False, "message": "All fields required"})

        books = load_books()
        new_id = max([b["id"] for b in books], default=0) + 1

        new_book = {
            "id": new_id,
            "title": title,
            "category": category,
            "borrowed": False,
            "otp_code": otp_code,
            "img": img,
        }

        books.append(new_book)
        save_books(books)

        return JsonResponse({"success": True, "book": new_book})

    return JsonResponse({"success": False, "message": "POST required"})


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    books = load_books()
    total = len(books)
    borrowed = sum(1 for b in books if b["borrowed"])
    returned = total - borrowed
    return render(
        request,
        "ALS/dashboard.html",
        {
            "books_data": json.dumps(books),
            "total_books": total,
            "borrowed_books": borrowed,
            "returned_books": returned,
        },
    )


def book_listing(request):
    path = os.path.join(settings.BASE_DIR, "books.json")
    with open(path, "r", encoding="utf-8") as f:
        books_data = json.load(f)
    return render(request, "book_listing.html", {"books_data": books_data})


@login_required
def account_settings(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserEmailForm(request.POST, instance=user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            return redirect("account_settings")
    else:
        profile_form = ProfileForm(instance=profile)
        user_form = UserEmailForm(instance=user)

    return render(
        request,
        "ALS/account.html",
        {"profile_form": profile_form, "user_form": user_form},
    )


@login_required
def books_view(request):
    BOOKS_JSON = os.path.join(os.path.dirname(__file__), "books.json")
    with open(BOOKS_JSON, "r") as f:
        books = json.load(f)
    context = {"books_data": json.dumps(books)}
    return render(request, "ALS/books.html", context)


import json
from django.http import JsonResponse

BOOKS_FILE = "path/to/books.json"


def dashboard_stats(request):
    with open(BOOKS_JSON, "r") as f:
        books = json.load(f)

    total_books = len(books)
    borrowed_books = sum(1 for b in books if b.get("borrowed"))
    available_books = total_books - borrowed_books
    returned_books = sum(1 for b in books if not b.get("borrowed"))

    return JsonResponse(
        {
            "total_books": total_books,
            "available_books": available_books,
            "borrowed_books": borrowed_books,
            "returned_books": returned_books,
            "books": [
                {
                    "title": b["title"],
                    "category": b["category"],
                    "status": "Borrowed" if b.get("borrowed") else "Available",
                }
                for b in books
            ],
        }
    )


def category_view(request):
    return render(request, "ALS/category.html")


def category_books(request, category_id):
    return render(request, "ALS/category.html", {"category_id": category_id})


def borrow_book_json(request):
    if request.method == "POST":
        data = json.loads(request.body)
        book_id = int(data.get("book_id"))
        otp = "123456"

        with open(BOOKS_JSON, "r") as f:
            books = json.load(f)

        for book in books:
            if book["id"] == book_id:
                if book.get("borrowed"):
                    return JsonResponse(
                        {"success": False, "message": "Book already borrowed"}
                    )
                book["borrowed"] = True
                book["otp_code"] = otp

        with open(BOOKS_JSON, "w") as f:
            json.dump(books, f, indent=2)

        return JsonResponse({"success": True, "message": "Book borrowed!", "otp": otp})


@csrf_exempt
def return_book_json(request):
    if request.method == "POST":
        data = json.loads(request.body)
        otp = data.get("otp")
        title = data.get("title").lower()
        books = load_books()
        for book in books:
            if (
                book["borrowed"]
                and book["title"].lower() == title
                and book["otp_code"] == otp
            ):
                book["borrowed"] = False
                save_books(books)
                return JsonResponse(
                    {"success": True, "message": f'Book "{book["title"]}" returned!'}
                )
        return JsonResponse(
            {"success": False, "message": "Invalid OTP or book not borrowed"}
        )
    return JsonResponse({"success": False, "message": "POST required"})


@csrf_exempt
def upload_image(request):
    """
    Accepts an uploaded image through POST and saves it.
    Returns the saved file path.
    """
    if request.method == "POST":
        if "image" not in request.FILES:
            return JsonResponse({"error": "No image uploaded"}, status=400)

        img = request.FILES["image"]

        save_dir = r"C:\Users\LLED\Documents\ALS\mysite\ALS\uploads"
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, img.name)

        with open(save_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)

        return JsonResponse({"success": True, "file_path": save_path})

    return JsonResponse({"error": "POST method required"}, status=400)


@login_required
def returned_books_view(request):
    student = request.user
    returned_books = BorrowRecord.objects.filter(user=student, returned=True).order_by(
        "-returned_at"
    )
    return render(
        request, "ALS/returned_books.html", {"returned_books": returned_books}
    )


@csrf_exempt
def receive_result(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        data = json.loads(request.body)
        record_id = data.get("borrow_record_id")
        student_id = data.get("student_id")
        book_title = data.get("book_title")
        photo_b64 = data.get("photo")

        try:
            record = BorrowRecord.objects.get(id=record_id, id_number=student_id)
        except BorrowRecord.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Borrow record not found."}
            )

        record.returned = True
        record.returned_at = timezone.now()
        record.notified = False

        if photo_b64:
            from django.core.files.base import ContentFile
            import base64, os

            returned_dir = r"C:\Users\LLED\Documents\ALS\returned_books"
            os.makedirs(returned_dir, exist_ok=True)

            format, imgstr = photo_b64.split(";base64,")
            ext = format.split("/")[-1]
            filename = f"{student_id}_{book_title}.{ext}"
            filepath = os.path.join(returned_dir, filename)

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(imgstr))
            record.photo.name = f"returned_books/{filename}"

        record.save()

        return JsonResponse(
            {
                "success": True,
                "message": f"Book '{record.book.title}' marked as returned!",
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@csrf_exempt
def ai_assistant(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        reply = nlp_match(user_message)
        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "POST method required"}, status=400)


LIBRARY_API_KEY = "YOUR_LIBRARY_DEVICE_KEY"
RETURNED_BOOKS_DIR = r"C:\Users\LLED\Documents\ALS\returned_books"
os.makedirs(RETURNED_BOOKS_DIR, exist_ok=True)


@csrf_exempt
def return_book(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST method required."})

    api_key = request.headers.get("x-api-key")
    if api_key != LIBRARY_API_KEY:
        return JsonResponse(
            {"success": False, "message": "Invalid API key."}, status=403
        )

    try:
        data = json.loads(request.body)
        record_id = data.get("borrow_record_id")
        name = data.get("borrower_name")
        book_title = data.get("book_title")
        student_id = data.get("student_id")
        course = data.get("course")
        photo_b64 = data.get("photo")

        try:
            record = BorrowRecord.objects.get(id=record_id, id_number=student_id)
        except BorrowRecord.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Borrow record not found."}
            )

        record.returned = True
        record.returned_at = timezone.now()
        record.notified = False

        if photo_b64:
            format, imgstr = photo_b64.split(";base64,")
            ext = format.split("/")[-1]
            filename = f"{student_id}_{book_title}.{ext}"
            filepath = os.path.join(RETURNED_BOOKS_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(imgstr))
            record.photo.name = f"returned_books/{filename}"

        record.save()

        return JsonResponse(
            {
                "success": True,
                "message": f"Book '{record.book.title}' successfully returned!",
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def check_return_status(request):
    student = request.user
    returned_books = BorrowRecord.objects.filter(
        user=student, returned=True, notified=False
    )

    response_data = []
    for record in returned_books:
    
        returned_str = (
            record.returned_at.strftime("%Y-%m-%d %H:%M:%S")
            if record.returned_at
            else None
        )

        response_data.append(
            {
                "book_title": record.book.title,
                "returned_at": returned_str,
            }
        )

        record.notified = True
        record.save()

    return JsonResponse({"returned_books": response_data})
