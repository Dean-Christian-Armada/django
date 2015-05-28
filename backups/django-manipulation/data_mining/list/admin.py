from django.contrib import admin
from . models import Userlevel, Members, Marines
from django.contrib.auth.models import User, Group


class MembersDates(admin.ModelAdmin):
	readonly_fields = ('date_added', 'date_modified')
	list_display = ('code', 'name', 'date_added', 'date_modified', 'IsActive')
	username = 'DSDAS'
	# prepopulated_fields = {'password': ('username',)}
	class Meta:
		verbose_name = "Staffs"
class MarinesDates(admin.ModelAdmin):
	pass

# Register your models here.
admin.site.register(Marines, MarinesDates)
admin.site.register(Members, MembersDates)
admin.site.register(Userlevel)
# admin.site.unregister(User)
admin.site.unregister(Group)