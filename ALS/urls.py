from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import add_book

urlpatterns = [
    # Auth
    path("", views.login_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.register_view, name="signup"),
    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/stats/", views.dashboard_stats, name="dashboard_stats"),
    # Books
    path("books/", views.books_view, name="books"),
    path(
        "books/listing/",
        TemplateView.as_view(template_name="ALS/book_listing.html"),
        name="book_listing",
    ),
    # Library
    path("library/", views.library_home, name="library_home"),
    # Categories
    path("category/", views.category_view, name="category"),
    path("category/<int:category_id>/", views.category_books, name="category_books"),
    # Borrow / Return (JSON only)
    path("borrow/<str:book_id>/", views.borrow_book_json, name="borrow_book"),
    path("borrow/", views.borrow_book_json, name="borrow_book_no_id"),
    path("return-json/", views.return_book_json, name="return_book_json"),
    path("return-book/", views.return_book, name="return_book"),
    # Images
    path("upload-image/", views.upload_image, name="upload_image"),
    # AI
    path("ai-assistant/", views.ai_assistant, name="ai_assistant"),
    # Borrow results / return status
    path("receive-result/", views.receive_result, name="receive_result"),
    path("check-return-status/", views.check_return_status, name="check_return_status"),
    path("returned-books/", views.returned_books_view, name="returned_books"),
    path("books/borrow-json/", views.borrow_book_json, name="borrow_book_json"),
    path("books/return-json/", views.return_book_json, name="return_book_json"),
    path("dashboard/stats/", views.dashboard_stats, name="dashboard_stats"),
    path("account/", views.account_settings, name="account_settings"),
    path("dashboard/admin/", views.admin_dashboard_view, name="admin_dashboard"),
    path("manage-students/", views.manage_students, name="manage_students"),
    path("manage-books/", views.manage_books, name="manage_books"),
    path("dashboard/", views.student_dashboard_view, name="student_dashboard"),
    path("manage-students/", views.manage_students, name="manage_students"),
    path("add_book/", add_book, name="add_book"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
