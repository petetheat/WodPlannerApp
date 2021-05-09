from django.contrib import admin

from .models import *

# TODO: Remove this later
admin.site.register(Question)
admin.site.register(Choice)

admin.site.register(Movement)
admin.site.register(Wod)
admin.site.register(WodMovement)
admin.site.register(StrengthMovement)
admin.site.register(Schemas)
