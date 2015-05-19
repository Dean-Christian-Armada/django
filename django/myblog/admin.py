from django.contrib import admin # import the command which allows us to register the model we created
from .models import Blog, Category, Author # import our models

# Register your models here.

class BlogAdmin(admin.ModelAdmin):
	#exclude = ['posted']
	prepopulated_fields = {'slug': ('title', )}
class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('title', )}
class AuthorAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name', )}

admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
