from django.contrib import admin
from . models import Userlevel, Members

class MembersDates(admin.ModelAdmin):
	readonly_fields = ('date_added', 'date_modified')
	list_display = ('code', 'name', 'date_added', 'date_modified', 'IsActive')

# Register your models here.
admin.site.register(Userlevel)
admin.site.register(Members, MembersDates)