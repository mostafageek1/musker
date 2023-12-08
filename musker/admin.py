from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Meep


# unregister groups
admin.site.unregister(Group)

# mix profile info into user info

class ProfileInline(admin.StackedInline):
    model = Profile

# extend user model

class UserAdmin(admin.ModelAdmin):
    model = User

    # display username fields on admin page

    fields = ["username", "email", "first_name", "last_name", ]
    inlines = [ProfileInline]

# unregister user
admin.site.unregister(User)

# reregister user
admin.site.register(User, UserAdmin)

# register meeps
admin.site.register(Meep)