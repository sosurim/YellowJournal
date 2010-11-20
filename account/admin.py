from django.contrib import admin
from models import *

class PhoneBookInline(admin.StackedInline):
	model = PhoneBook
	can_delete = True
	extra = 0

class AddressBookInline(admin.StackedInline):
	model = AddressBook
	can_delete = True
	extra = 0
	
class CustomUserAdmin(admin.ModelAdmin):
	inlines = [PhoneBookInline, AddressBookInline, ]

admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
#admin.site.register(RegistrationProfile)