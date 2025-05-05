from django.contrib import admin

from phx.admin import phx_admin

from .models import FooterSection, FooterLink


class FooterLinkInline(admin.StackedInline):
    extra = 1
    max_num = 3
    model = FooterLink


class FooterAdmin(admin.ModelAdmin):
    inlines = [FooterLinkInline]

    def has_add_permission(self, request):
        # Don't allow more than three sections to be added
        # to the footer, otherwise it will look cluttered.
        if FooterSection.objects.count() >= 3:
            return False

        return super().has_add_permission(request)
    pass


phx_admin.register(FooterSection, FooterAdmin)
