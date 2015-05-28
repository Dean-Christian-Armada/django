from django.contrib import admin
from . models import Userlevel, Members, Marines
from django.contrib.auth.models import User, Group


class MembersDates(admin.ModelAdmin):
	readonly_fields = ('date_added', 'date_modified', 'old_password')
	list_display = ('code', 'name', 'date_added', 'date_modified', 'IsActive')
	list_filter = ('gender', 'title', 'city')
	list_select_related = ('userlevel', 'marines')
	search_fields = ('country', 'name', 'code')
	ordering = ('name',)
	title = 'Staffs'
	# prepopulated_fields = {'password': ('username',)}
	class Meta:
		verbose_name = "Staffs"
	def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
		formfield = super(MembersDates, self).formfield_for_foreignkey(db_field, request, **kwargs)
		if db_field.name == 'userlevel':
			formfield.queryset = Userlevel.objects.filter(userlevel='staff')
		return formfield
	# def lookups(self, request, model_admin):
	# 	queryset = model_admin.queryset(request).filter(Members__city='Quezon City')
	# 	return queryset.values_list('Members__pk','Members__name').order_by('Members__name')

	# Shows only staffs
	def get_queryset(self, request):
		qs = super(MembersDates, self).get_queryset(request)
		return qs.filter(userlevel='1')

class MarinesDates(admin.ModelAdmin):
	pass

# Register your models here.
# admin.site.register(Marines, MarinesDates)
admin.site.register(Members, MembersDates)
# admin.site.register(Userlevel)
admin.site.unregister(User)
admin.site.unregister(Group)