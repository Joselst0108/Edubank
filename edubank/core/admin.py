from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Institution, User, UserRole, Account, Transaction, Loan

# To display UserRoles inline in the User admin page
class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1

# To display Account inline in the User admin page
class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserRoleInline, AccountInline)
    # Add profile_picture to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('profile_picture',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('profile_picture',)}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Institution)
admin.site.register(UserRole)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Loan)
