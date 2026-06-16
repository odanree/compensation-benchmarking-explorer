import pytest
from django.test import RequestFactory

from apps.compensation.schema import schema
from apps.compensation.tests.factories import CostBandFactory


class _Context:
    """Wraps a request so info.context.request works in execute_sync tests."""
    def __init__(self, request):
        self.request = request


def make_context(authenticated=False):
    rf = RequestFactory()
    request = rf.get("/graphql/")
    if authenticated:
        from django.contrib.auth.models import User

        user, _ = User.objects.get_or_create(username="test_auth_user")
        request.user = user
    else:
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()
    return _Context(request)


@pytest.mark.django_db
class TestCostBandsQuery:
    def test_returns_results(self):
        CostBandFactory.create_batch(5, system_size_range="5-8 kW")
        result = schema.execute_sync(
            """
            query {
                costBands(first: 10) {
                    edges { node { systemSizeRange panelTier p50 } }
                    pageInfo { hasNextPage }
                    totalCount
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["costBands"]["totalCount"] == 5
        assert len(result.data["costBands"]["edges"]) == 5

    def test_p90_hidden_for_unauthenticated(self):
        CostBandFactory.create()
        result = schema.execute_sync(
            """
            query {
                costBands(first: 1) {
                    edges { node { p90 } }
                }
            }
            """,
            context_value=make_context(authenticated=False),
        )
        assert not result.errors
        assert result.data["costBands"]["edges"][0]["node"]["p90"] is None

    def test_p90_visible_for_authenticated(self):
        CostBandFactory.create(p90=4.500)
        result = schema.execute_sync(
            """
            query {
                costBands(first: 1) {
                    edges { node { p90 } }
                }
            }
            """,
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        assert result.data["costBands"]["edges"][0]["node"]["p90"] == pytest.approx(4.5)

    def test_cursor_pagination(self):
        CostBandFactory.create_batch(10)
        result1 = schema.execute_sync(
            """
            query {
                costBands(first: 5) {
                    edges { cursor node { id } }
                    pageInfo { hasNextPage endCursor }
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result1.errors
        assert result1.data["costBands"]["pageInfo"]["hasNextPage"] is True

        cursor = result1.data["costBands"]["pageInfo"]["endCursor"]
        result2 = schema.execute_sync(
            f"""
            query {{
                costBands(first: 5, after: "{cursor}") {{
                    edges {{ node {{ id }} }}
                    pageInfo {{ hasNextPage hasPreviousPage }}
                    totalCount
                }}
            }}
            """,
            context_value=make_context(),
        )
        assert not result2.errors
        assert result2.data["costBands"]["pageInfo"]["hasPreviousPage"] is True
        assert result2.data["costBands"]["totalCount"] == 10

    def test_filter_by_system_size_range(self):
        CostBandFactory.create(system_size_range="5-8 kW", panel_tier="standard", installer_type="local")
        CostBandFactory.create(system_size_range="8-12 kW", panel_tier="standard", installer_type="regional")
        result = schema.execute_sync(
            """
            query {
                costBands(filters: { systemSizeRange: "5-8 kW" }) {
                    totalCount
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["costBands"]["totalCount"] == 1

    def test_filter_by_installer_type(self):
        CostBandFactory.create(installer_type="local", system_size_range="3-5 kW")
        CostBandFactory.create(installer_type="national", system_size_range="5-8 kW")
        result = schema.execute_sync(
            """
            query {
                costBands(filters: { installerType: "local" }) {
                    totalCount
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["costBands"]["totalCount"] == 1

    def test_available_size_ranges(self):
        result = schema.execute_sync(
            """
            query { availableSizeRanges }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert "5-8 kW" in result.data["availableSizeRanges"]
        assert "8-12 kW" in result.data["availableSizeRanges"]

    def test_available_locations(self):
        CostBandFactory.create(location="California", system_size_range="3-5 kW", panel_tier="standard", installer_type="local")
        CostBandFactory.create(location="Texas", system_size_range="5-8 kW", panel_tier="standard", installer_type="regional")
        result = schema.execute_sync(
            """
            query { availableLocations }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert "California" in result.data["availableLocations"]

    def test_single_band_query(self):
        band = CostBandFactory.create(p50=3.500)
        result = schema.execute_sync(
            f"""
            query {{
                costBand(id: "{band.pk}") {{
                    id
                    systemSizeRange
                    p50
                }}
            }}
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["costBand"]["p50"] == pytest.approx(3.5)

    def test_single_band_not_found(self):
        result = schema.execute_sync(
            """
            query {
                costBand(id: "99999") {
                    id
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["costBand"] is None


CREATE_BAND_MUTATION = """
    mutation CreateBand($input: CostBandInput!) {
        createBand(input: $input) {
            ... on CreateBandSuccess {
                band {
                    id
                    systemSizeRange
                    panelTier
                    location
                    installerType
                    p25
                    p50
                    p75
                    p90
                    sampleSize
                }
            }
            ... on CreateBandError {
                messages
            }
        }
    }
"""

VALID_INPUT = {
    "systemSizeRange": "5-8 kW",
    "panelTier": "premium",
    "location": "California",
    "installerType": "local",
    "p25": 3.25,
    "p50": 3.70,
    "p75": 4.15,
    "p90": 4.65,
    "sampleSize": 95,
}


@pytest.mark.django_db
class TestCreateBandMutation:
    def test_authenticated_user_can_create_band(self):
        result = schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": VALID_INPUT},
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        data = result.data["createBand"]
        assert "band" in data
        assert data["band"]["systemSizeRange"] == "5-8 kW"
        assert data["band"]["p50"] == pytest.approx(3.7)
        assert data["band"]["p90"] == pytest.approx(4.65)  # authenticated, so p90 visible

    def test_unauthenticated_user_cannot_create_band(self):
        result = schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": VALID_INPUT},
            context_value=make_context(authenticated=False),
        )
        assert result.errors
        assert "logged in" in result.errors[0].message

    def test_duplicate_band_returns_error(self):
        schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": VALID_INPUT},
            context_value=make_context(authenticated=True),
        )
        result = schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": VALID_INPUT},
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        data = result.data["createBand"]
        assert "messages" in data
        assert "already exists" in data["messages"][0]

    def test_invalid_percentile_order_returns_error(self):
        bad_input = {**VALID_INPUT, "p25": 5.0, "p50": 2.0}
        result = schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": bad_input},
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        data = result.data["createBand"]
        assert "messages" in data
        assert any("p25" in m or "Percentile" in m for m in data["messages"])

    def test_invalid_installer_type_returns_error(self):
        bad_input = {**VALID_INPUT, "installerType": "franchise"}
        result = schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": bad_input},
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        data = result.data["createBand"]
        assert "messages" in data
        assert any("installer_type" in m for m in data["messages"])

    def test_invalid_panel_tier_returns_error(self):
        bad_input = {**VALID_INPUT, "panelTier": "ultra-premium"}
        result = schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": bad_input},
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        data = result.data["createBand"]
        assert "messages" in data
        assert any("panel_tier" in m for m in data["messages"])

    def test_band_persisted_to_database(self):
        from apps.compensation.models import CostBand

        assert CostBand.objects.count() == 0
        schema.execute_sync(
            CREATE_BAND_MUTATION,
            variable_values={"input": VALID_INPUT},
            context_value=make_context(authenticated=True),
        )
        assert CostBand.objects.count() == 1
        band = CostBand.objects.first()
        assert float(band.p90) == pytest.approx(4.65)
