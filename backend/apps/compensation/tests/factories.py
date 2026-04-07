import factory

from apps.compensation.models import CompensationBand


class CompensationBandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompensationBand

    role = factory.Sequence(lambda n: f"Software Engineer {n}")
    level = factory.Sequence(lambda n: ["IC3", "IC4", "IC5", "IC6", "M4"][n % 5])
    location = factory.Sequence(lambda n: ["San Francisco Bay Area", "New York Metro", "Seattle Metro", "Austin Metro", "Remote"][n % 5])
    company_size = CompensationBand.CompanySize.ENTERPRISE
    p25 = 160000
    p50 = 185000
    p75 = 215000
    p90 = 255000
    sample_size = 50
