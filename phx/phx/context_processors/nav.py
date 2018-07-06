from django.urls import reverse


def nav(request):
    items = [
        {
            'linkUrl': '/about/',
            'linkText': 'About'
        },
        {
            'linkUrl': reverse('fixtures-index'),
            'linkText': 'Fixtures'
        },
        {
            'linkUrl': reverse('results-index'),
            'linkText': 'Results'
        },
        {
            'linkUrl': '/training/',
            'linkText': 'Training'
        },
        {
            'linkUrl': reverse('news-list'),
            'linkText': 'News',
        },
        {
            'linkUrl': '/events/',
            'linkText': 'Events'
        },
        {
            'linkUrl': '/membership/',
            'linkText': 'Membership'
        },
        {
            'linkUrl': reverse('contact-index'),
            'linkText': 'Contact',
        }
    ]

    # identify parent section of deep links
    request_path = request.get_full_path()
    section_name = request_path.split('/')[1]
    section = '/{0}/'.format(section_name)

    nav = [
        {
            'linkText': item['linkText'],
            'linkUrl': item['linkUrl'],
            'active': (item['linkUrl'] == section),
            'contact': (item['linkText'] == 'Contact')
        }
        for item in items
    ]

    return {
        'nav': nav
    }