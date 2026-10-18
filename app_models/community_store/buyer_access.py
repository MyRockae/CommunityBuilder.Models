"""Purchase eligibility and course entitlement helpers shared by Main API and Payment."""

from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from app_models.community.models import CommunityMember, CommunityGroupAccess
from app_models.community_store.models import (
    StoreBuyerAudience,
    StoreProduct,
    StoreProductKind,
    StorePurchase,
)


def is_approved_community_member(user, community) -> bool:
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    try:
        membership = community.community_members.get(user=user)
    except CommunityMember.DoesNotExist:
        return False
    if membership.is_blocked or membership.role == 'applicant':
        return False
    return True


def user_has_completed_course_purchase(user, course) -> bool:
    if not user or not getattr(user, 'is_authenticated', False) or course is None:
        return False
    return StorePurchase.objects.filter(
        buyer_user=user,
        status=StorePurchase.STATUS_COMPLETED,
        product__product_kind=StoreProductKind.COURSE,
        product__course_id=course.pk,
    ).exists()


def user_has_course_group_access(user, course, community) -> bool:
    """Active CommunityGroupAccess overlap with course.community_groups (no membership required for the query)."""
    if not user or not getattr(user, 'is_authenticated', False) or course is None:
        return False
    group_ids = list(course.community_groups.values_list('id', flat=True))
    if not group_ids:
        return False
    now = timezone.now()
    return CommunityGroupAccess.objects.filter(
        user=user,
        community=community,
        community_group_id__in=group_ids,
        is_active=True,
    ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now)).exists()


def user_owns_course(user, course, community) -> bool:
    """Entitled via completed course purchase or active group access (owners checked separately by callers)."""
    if user_has_completed_course_purchase(user, course):
        return True
    return user_has_course_group_access(user, course, community)


def active_course_sale_product(course) -> StoreProduct | None:
    if course is None:
        return None
    return (
        StoreProduct.objects.filter(
            product_kind=StoreProductKind.COURSE,
            course_id=course.pk,
            is_active=True,
            store__is_active=True,
        )
        .select_related('store')
        .prefetch_related('prices')
        .first()
    )


def viewer_may_buy_store_product(product: StoreProduct, user, community) -> tuple[bool, str | None]:
    """
    Whether this viewer may start checkout for the product.
    Courses always require a signed-in user.
    """
    kind = product.product_kind or StoreProductKind.FILE
    audience = product.buyer_audience or StoreBuyerAudience.ANYONE
    authenticated = bool(user and getattr(user, 'is_authenticated', False))

    if kind == StoreProductKind.COURSE:
        if not authenticated:
            return False, 'Sign in to buy this course.'
        if user_owns_course(user, product.course, community):
            return False, 'You already have access to this course.'
        # Also reject duplicate purchase row
        if StorePurchase.objects.filter(
            product=product,
            buyer_user=user,
            status=StorePurchase.STATUS_COMPLETED,
        ).exists():
            return False, 'You already own this product.'

    is_member = is_approved_community_member(user, community) if authenticated else False

    if audience == StoreBuyerAudience.MEMBERS:
        if not is_member:
            return False, 'Only community members can buy this product.'
    elif audience == StoreBuyerAudience.NON_MEMBERS:
        if not authenticated:
            return False, 'Sign in to buy this product.'
        if is_member:
            return False, 'This product is only available to non-members.'

    return True, None


def viewer_can_buy_course(user, course, community, sale_product: StoreProduct | None = None) -> bool:
    product = sale_product if sale_product is not None else active_course_sale_product(course)
    if not product or not product.is_active:
        return False
    ok, _ = viewer_may_buy_store_product(product, user, community)
    return ok
