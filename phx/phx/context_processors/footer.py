from footer.models import FooterSection


def footer_data(request):
    return {
        'footer_sections':
        FooterSection.objects.prefetch_related('links').all()
    }
