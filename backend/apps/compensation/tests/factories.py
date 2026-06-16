import factory

from apps.compensation.models import CostBand


class CostBandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CostBand

    system_size_range = factory.Sequence(
        lambda n: ["3-5 kW", "5-8 kW", "8-12 kW", "12 kW+"][n % 4]
    )
    panel_tier = factory.Sequence(
        lambda n: ["standard", "premium", "premium-plus"][n % 3]
    )
    location = factory.Sequence(
        lambda n: ["California", "Texas", "Florida", "Arizona", "New York"][n % 5]
    )
    installer_type = CostBand.InstallerType.LOCAL
    p25 = 2.800
    p50 = 3.200
    p75 = 3.700
    p90 = 4.200
    sample_size = 50
