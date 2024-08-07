from django.contrib import admin

from .models import *




class FiliereAdmin(admin.ModelAdmin):
    list_display = ('id','name','semestres')

admin.site.register(Filiere,FiliereAdmin)
admin.site.register(Cours)
admin.site.register(Emploi)
admin.site.register(Paiement)

# Matieres
class MatAdmin(admin.ModelAdmin):
    list_display = ('id','name','filiere','code',)

admin.site.register(Matiere,MatAdmin)