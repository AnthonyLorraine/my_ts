from django.contrib import admin
from main.models import Employee, Penalty, PenaltyType

admin.site.register(Employee)
admin.site.register(Penalty)
admin.site.register(PenaltyType)