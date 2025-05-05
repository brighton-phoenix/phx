from django.db import models


class FooterLink(models.Model):
    text = models.CharField(max_length=100)
    path = models.CharField(
        max_length=100,
        help_text="""
        <p>An internal path, a download link or an external link</p>
        e.g.
        <ul>
          <li>/contact/<li/>
          <li>/media/2023-01-01-policy.pdf</li>
          <li>mailto:club@brightonphoenix.org.uk</li>
        <ul/>
        """)
    order = models.PositiveIntegerField(default=0)

    section = models.ForeignKey(
        'FooterSection',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='links'
    )

    def __str__(self):
        return self.text


class FooterSection(models.Model):
    header = models.CharField(max_length=100)
    sub_header = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.header
