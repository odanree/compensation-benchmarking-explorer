import base64
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.types import Info

from apps.compensation.models import CompensationBand


def encode_cursor(pk: int) -> str:
    return base64.b64encode(f"CompensationBand:{pk}".encode()).decode()


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
class CompensationBandType:
    id: strawberry.ID
    role: str
    level: str
    location: str
    company_size: str
    p25: float
    p50: float
    p75: float
    p90: Optional[float]
    sample_size: int
    last_updated: datetime

    @staticmethod
    def from_model(band: CompensationBand, authenticated: bool) -> "CompensationBandType":
        return CompensationBandType(
            id=strawberry.ID(str(band.pk)),
            role=band.role,
            level=band.level,
            location=band.location,
            company_size=band.company_size,
            p25=float(band.p25),
            p50=float(band.p50),
            p75=float(band.p75),
            p90=float(band.p90) if authenticated else None,
            sample_size=band.sample_size,
            last_updated=band.last_updated,
        )


@strawberry.type
class CompensationBandEdge:
    node: CompensationBandType
    cursor: str


@strawberry.type
class CompensationBandConnection:
    edges: list[CompensationBandEdge]
    page_info: PageInfo
    total_count: int


@strawberry.input
class CompensationBandFilter:
    role: Optional[str] = None
    level: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    min_p50: Optional[float] = None
    max_p50: Optional[float] = None


def apply_filters(qs, filters: Optional[CompensationBandFilter]):
    if filters is None:
        return qs
    if filters.role:
        qs = qs.filter(role__iexact=filters.role)
    if filters.level:
        qs = qs.filter(level__iexact=filters.level)
    if filters.location:
        qs = qs.filter(location__iexact=filters.location)
    if filters.company_size:
        qs = qs.filter(company_size__iexact=filters.company_size)
    if filters.min_p50 is not None:
        qs = qs.filter(p50__gte=filters.min_p50)
    if filters.max_p50 is not None:
        qs = qs.filter(p50__lte=filters.max_p50)
    return qs


@strawberry.type
class Query:
    @strawberry.field
    def compensation_bands(
        self,
        info: Info,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        filters: Optional[CompensationBandFilter] = None,
    ) -> CompensationBandConnection:
        authenticated = info.context.request.user.is_authenticated
        qs = CompensationBand.objects.all().order_by("pk")
        qs = apply_filters(qs, filters)

        total_count = qs.count()

        if after:
            after_pk = decode_cursor(after)
            qs = qs.filter(pk__gt=after_pk)

        page_size = min(first or 20, 100)
        # Fetch one extra to know if there's a next page
        items = list(qs[:page_size + 1])
        has_next = len(items) > page_size
        items = items[:page_size]

        edges = [
            CompensationBandEdge(
                node=CompensationBandType.from_model(band, authenticated),
                cursor=encode_cursor(band.pk),
            )
            for band in items
        ]

        return CompensationBandConnection(
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
    def compensation_band(
        self, info: Info, id: strawberry.ID
    ) -> Optional[CompensationBandType]:
        authenticated = info.context.request.user.is_authenticated
        try:
            band = CompensationBand.objects.get(pk=int(id))
            return CompensationBandType.from_model(band, authenticated)
        except CompensationBand.DoesNotExist:
            return None

    @strawberry.field
    def available_roles(self) -> list[str]:
        return list(
            CompensationBand.objects.values_list("role", flat=True)
            .distinct()
            .order_by("role")
        )

    @strawberry.field
    def available_locations(self) -> list[str]:
        return list(
            CompensationBand.objects.values_list("location", flat=True)
            .distinct()
            .order_by("location")
        )


schema = strawberry.Schema(query=Query)
