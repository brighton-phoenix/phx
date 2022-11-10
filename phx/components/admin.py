import nested_admin
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer


class AbstractComponentAdmin(nested_admin.NestedStackedInline):
    extra = 0
    max_num = 1

    class Meta:
        abstract = True


class AbstractEditorialAdmin(AbstractComponentAdmin):

    class Meta:
        abstract = True


class AbstractEmbedAdmin(AbstractComponentAdmin):

    class Meta:
        abstract = True


class AbstractFeatureAdmin(AbstractComponentAdmin):
    readonly_fields = ['current_image']

    def current_image(self, obj):
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {'size': (200, 200)}
        return format_html('<img src="/media/{0}" />'.format(
            thumbnailer.get_thumbnail(thumbnail_options)))

    class Meta:
        abstract = True


class AbstractImageAdmin(AbstractComponentAdmin):
    readonly_fields = ['current_image']

    def current_image(self, obj):
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {'size': (200, 200)}
        return format_html('<img src="/media/{0}" />'.format(
            thumbnailer.get_thumbnail(thumbnail_options)))

    class Meta:
        abstract = True


class AbstractListItemsAdmin(AbstractComponentAdmin):

    class Meta:
        abstract = True


class AbstractListItemAdmin(AbstractComponentAdmin):
    max_num = 3
    readonly_fields = ['current_image']

    def current_image(self, obj):
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {'size': (200, 200)}
        return format_html('<img src="/media/{0}" />'.format(
            thumbnailer.get_thumbnail(thumbnail_options)))

    class Meta:
        abstract = True


class AbstractProfileAdmin(AbstractComponentAdmin):

    class Meta:
        abstract = True


class AbstractProfileMemberAdmin(AbstractComponentAdmin):
    max_num = 32
    readonly_fields = ['current_image']

    def current_image(self, obj):
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {'size': (200, 200)}
        return format_html('<img src="/media/{0}" />'.format(
            thumbnailer.get_thumbnail(thumbnail_options)))

    class Meta:
        abstract = True


class AbstractQuoteAdmin(AbstractComponentAdmin):
    readonly_fields = ['current_image']

    def current_image(self, obj):
        thumbnailer = get_thumbnailer(obj.image)
        thumbnail_options = {'size': (200, 200)}
        return format_html('<img src="/media/{0}" />'.format(
            thumbnailer.get_thumbnail(thumbnail_options)))

    class Meta:
        abstract = True


class AbstractTableAdmin(AbstractComponentAdmin):

    class Meta:
        abstract = True
