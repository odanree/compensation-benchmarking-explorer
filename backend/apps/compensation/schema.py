import base64
from datetime import datetime
from typing import Annotated, Optional, Union

import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from apps.compensation.models import CostBand


class IsAuthenticated(BasePermission):
    message = "You must be logged in to perform this action."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        return info.context.request.user.is_authenticated


def encode_cursor(pk: int) -> str:
    return base64.b64encode(f"CostBand:{pk}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    decoded = base64.b64decode(cursor.encode()).decode()
    return int(decoded.split(":")[1])


@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]


@strawberry.type
class CostBandType:
    id: strawberry.ID
    system_size_range: str
    panel_tier: str
    location: str
    installer_type: str
    p25: float
    p50: float
    p75: float
    p90: Optional[float]
    sample_size: int
    last_updated: datetime

    @staticmethod
    def from_model(band: CostBand, authenticated: bool) -> "CostBandType":
        return CostBandType(
            id=strawberry.ID(str(band.pk)),
            system_size_range=band.system_size_range,
            panel_tier=band.panel_tier,
            location=band.location,
            installer_type=band.installer_type,
            p25=float(band.p25),
            p50=float(band.p50),
            p75=float(band.p75),
            p90=float(band.p90) if authenticated else None,
            sample_size=band.sample_size,
            last_updated=band.last_updated,
        )


@strawberry.type
class CostBandEdge:
    node: CostBandType
    cursor: str


@strawberry.type
class CostBandConnection:
    edges: list[CostBandEdge]
    page_info: PageInfo
    total_count: int


@strawberry.input
class CostBandFilter:
    system_size_range: Optional[str] = None
    panel_tier: Optional[str] = None
    location: Optional[str] = None
    installer_type: Optional[str] = None
    min_p50: Optional[float] = None
    max_p50: Optional[float] = None


def apply_filters(qs, filters: Optional[CostBandFilter]):
    if filters is None:
        return qs
    if filters.system_size_range:
        qs = qs.filter(system_size_range__iexact=filters.system_size_range)
    if filters.panel_tier:
        qs = qs.filter(panel_tier__iexact=filters.panel_tier)
    if filters.location:
        qs = qs.filter(location__iexact=filters.location)
    if filters.installer_type:
        qs = qs.filter(installer_type__iexact=filters.installer_type)
    if filters.min_p50 is not None:
        qs = qs.filter(p50__gte=filters.min_p50)
    if filters.max_p50 is not None:
        qs = qs.filter(p50__lte=filters.max_p50)
    return qs


@strawberry.type
class Query:
    @strawberry.field
    def cost_bands(
        self,
        info: Info,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        filters: Optional[CostBandFilter] = None,
    ) -> CostBandConnection:
        authenticated = info.context.request.user.is_authenticated
        qs = CostBand.objects.all().order_by("pk")
        qs = apply_filters(qs, filters)

        total_count = qs.count()

        if after:
            after_pk = decode_cursor(after)
            qs = qs.filter(pk__gt=after_pk)

        page_size = min(first or 20, 100)
        items = list(qs[:page_size + 1])
        has_next = len(items) > page_size
        items = items[:page_size]

        edges = [
            CostBandEdge(
                node=CostBandType.from_model(band, authenticated),
                cursor=encode_cursor(band.pk),
            )
            for band in items
        ]

        return CostBandConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next,
                has_previous_page=after is not None,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=total_count,
        )

    @strawberry.field
    def cost_band(
        self, info: Info, id: strawberry.ID
    ) -> Optional[CostBandType]:
        authenticated = info.context.request.user.is_authenticated
        try:
            band = CostBand.objects.get(pk=int(id))
            return CostBandType.from_model(band, authenticated)
        except CostBand.DoesNotExist:
            return None

    @strawberry.field
    def available_locations(self) -> list[str]:
        return list(
            CostBand.objects.values_list("location", flat=True)
            .distinct()
            .order_by("location")
        )

    @strawberry.field
    def available_size_ranges(self) -> list[str]:
        return ["3-5 kW", "5-8 kW", "8-12 kW", "12 kW+"]

    @strawberry.field
    def available_panel_tiers(self) -> list[str]:
        return ["standard", "premium", "premium-plus"]

    @strawberry.field
    def available_installer_types(self) -> list[str]:
        return ["local", "regional", "national", "utility"]


@strawberry.input
class CostBandInput:
    system_size_range: str
    panel_tier: str
    location: str
    installer_type: str
    p25: float
    p50: float
    p75: float
    p90: float
    sample_size: int = 0

    def validate(self) -> list[str]:
        errors = []
        valid_tiers = {"standard", "premium", "premium-plus"}
        valid_installers = {c.value for c in CostBand.InstallerType}
        valid_size_ranges = {"3-5 kW", "5-8 kW", "8-12 kW", "12 kW+"}

        if self.system_size_range not in valid_size_ranges:
            errors.append(
                f"system_size_range must be one of: {', '.join(sorted(valid_size_ranges))}."
            )
        if self.panel_tier not in valid_tiers:
            errors.append(
                f"panel_tier must be one of: {', '.join(sorted(valid_tiers))}."
            )
        if not self.location.strip():
            errors.append("location must not be blank.")
        if self.installer_type not in valid_installers:
            errors.append(
                f"installer_type must be one of: {', '.join(sorted(valid_installers))}."
            )
        if not (0 < self.p25 <= self.p50 <= self.p75 <= self.p90):
            errors.append("Percentiles must satisfy 0 < p25 <= p50 <= p75 <= p90.")
        if self.sample_size < 0:
            errors.append("sample_size must be >= 0.")
        return errors


@strawberry.type
class CreateBandSuccess:
    band: CostBandType


@strawberry.type
class CreateBandError:
    messages: list[str]


CreateBandResult = Annotated[
    Union[CreateBandSuccess, CreateBandError],
    strawberry.union("CreateBandResult"),
]


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_band(self, info: Info, input: CostBandInput) -> CreateBandResult:
        errors = input.validate()
        if errors:
            return CreateBandError(messages=errors)

        band, created = CostBand.objects.get_or_create(
            system_size_range=input.system_size_range,
            panel_tier=input.panel_tier,
            location=input.location.strip(),
            installer_type=input.installer_type,
            defaults={
                "p25": input.p25,
                "p50": input.p50,
                "p75": input.p75,
                "p90": input.p90,
                "sample_size": input.sample_size,
            },
        )

        if not created:
            return CreateBandError(
                messages=[
                    f"A band for '{input.system_size_range}' / '{input.panel_tier}' / "
                    f"'{input.location}' / '{input.installer_type}' already exists. "
                    "Use updateBand to modify existing records."
                ]
            )

        authenticated = info.context.request.user.is_authenticated
        return CreateBandSuccess(band=CostBandType.from_model(band, authenticated))


schema = strawberry.Schema(query=Query, mutation=Mutation)
