
from factory.fuzzy import FuzzyText
from factory_djoy import CleanModelFactory

from ..models import FooterSection, FooterLink


class FooterLinkFactory(CleanModelFactory):
    text = FuzzyText()
    path = FuzzyText()

    class Meta:
        model = FooterLink


class FooterSectionFactory(CleanModelFactory):
    header = FuzzyText()
    sub_header = FuzzyText()

    class Meta:
        model = FooterSection
