from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Account, EmailVerification, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    readonly_fields = ("avatar_preview",)
    fieldsets = (
        (None, {"fields": ("email", "password", "username")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name", "profile_picture", "avatar_preview")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = ("email", "first_name", "last_name", "is_staff", "avatar_thumb")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    @admin.display(description="Preview")
    def avatar_preview(self, obj):
        if obj and obj.profile_picture:
            return format_html('<img src="{}" style="max-height:120px;border-radius:8px;" />', obj.profile_picture.url)
        return "— sem imagem —"

    @admin.display(description="Avatar", ordering="profile_picture")
    def avatar_thumb(self, obj):
        pic = getattr(obj, "profile_picture", None)
        if not pic:
            return ""
        try:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />',
                pic.url,
            )
        except Exception:
            return ""


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "email_verified", "created_at")
    list_filter = ("provider", "email_verified")


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "expires_at", "verified_at")
    readonly_fields = ("token",)
