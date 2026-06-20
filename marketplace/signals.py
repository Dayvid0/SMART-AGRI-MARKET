"""
marketplace/signals.py

Auto-updates FarmerProfile.rating_average and total_sales whenever:
  - A Review is saved or deleted
  - An Order status changes to 'completed'
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

from accounts.models import FarmerProfile


def _recalculate_farmer_stats(farmer_user):
    """
    Recalculate and persist rating_average + total_sales for a farmer.
    Safe to call repeatedly — always reads fresh from DB.
    """
    try:
        profile = farmer_user.farmer_profile
    except FarmerProfile.DoesNotExist:
        return

    # Import here to avoid circular import at module level
    from marketplace.models import Review
    from orders.models import Order

    reviews = Review.objects.filter(farmer=farmer_user)
    agg = reviews.aggregate(avg=Avg('rating'))
    profile.rating_average = round(agg['avg'] or 0, 2)
    profile.total_sales = Order.objects.filter(
        farmer=farmer_user, status='completed'
    ).count()
    profile.save(update_fields=['rating_average', 'total_sales'])


@receiver(post_save, sender='marketplace.Review')
def review_saved(sender, instance, **kwargs):
    """Recalculate farmer stats whenever a review is created or updated."""
    _recalculate_farmer_stats(instance.farmer)


@receiver(post_delete, sender='marketplace.Review')
def review_deleted(sender, instance, **kwargs):
    """Recalculate farmer stats when a review is removed."""
    _recalculate_farmer_stats(instance.farmer)


@receiver(post_save, sender='orders.Order')
def order_status_changed(sender, instance, **kwargs):
    """
    When an order reaches 'completed' status, update the farmer's total_sales.
    This catches status changes made through admin, API, or views.
    """
    if instance.status == 'completed':
        _recalculate_farmer_stats(instance.farmer)
