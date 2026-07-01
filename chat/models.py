from django.db import models
from accounts.models import User
from marketplace.models import Product


class ChatThread(models.Model):
    """
    A negotiation conversation between a buyer and a seller about a specific product.
    One thread per buyer-product pair — prevents spam and keeps conversations focused.
    Inspired by the SafeBoda model: chat opens once buyer expresses interest in a product.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='chat_threads',
        help_text="The product being negotiated"
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_threads_as_buyer',
        help_text="The user who initiated the negotiation"
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_threads_as_seller',
        help_text="The farmer/seller of the product"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat Thread"
        verbose_name_plural = "Chat Threads"
        ordering = ['-updated_at']
        # One thread per buyer-product pair
        unique_together = ['product', 'buyer']

    def __str__(self):
        return f"Thread: {self.buyer.username} ↔ {self.seller.username} | {self.product.name}"

    def get_unread_count(self, user):
        """Return number of unread messages for a given user in this thread."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def get_last_message(self):
        return self.messages.order_by('-sent_at').first()

    def get_active_offer(self):
        """Return the latest pending price offer in this thread, if any."""
        return self.messages.filter(
            msg_type='offer', offer_status='pending'
        ).order_by('-sent_at').first()


class ChatMessage(models.Model):
    """
    A single message within a negotiation thread.
    Can be a plain text message OR a formal price offer (msg_type='offer').
    Admins can read all messages from the Django Admin panel.
    """
    MSG_TYPE_CHOICES = [
        ('text', 'Text'),
        ('offer', 'Price Offer'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_rejected', 'Offer Rejected'),
        ('deal_done', 'Deal Finalised'),
    ]
    OFFER_STATUS_CHOICES = [
        ('pending', 'Pending Response'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('superseded', 'Superseded by New Offer'),
    ]

    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_chat_messages'
    )
    content = models.TextField(
        help_text="Message content"
    )
    msg_type = models.CharField(
        max_length=20,
        choices=MSG_TYPE_CHOICES,
        default='text',
        db_index=True
    )

    # ---- Price Offer fields (populated only when msg_type='offer') ----
    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Proposed price per unit (UGX)"
    )
    offer_quantity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Proposed quantity for this offer"
    )
    offer_status = models.CharField(
        max_length=20,
        choices=OFFER_STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Lifecycle status of this offer message"
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Has the recipient read this message?"
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ['sent_at']

    def __str__(self):
        if self.msg_type == 'offer':
            return f"{self.sender.username} offered UGX {self.offer_price}/{self.thread.product.unit}"
        return f"{self.sender.username}: {self.content[:50]}"

    @property
    def offer_total(self):
        if self.offer_price and self.offer_quantity:
            return self.offer_price * self.offer_quantity
        return None


class NegotiatedDeal(models.Model):
    """
    Records a finalised price deal after a buyer accepts an offer.
    Linked to the offer message and used to create an order at the agreed price.
    Admins see all deals — this is the paper trail of every negotiated price.
    """
    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name='deals'
    )
    offer_message = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='deal'
    )
    agreed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Agreed price per unit (UGX)"
    )
    agreed_quantity = models.IntegerField(
        help_text="Agreed quantity"
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='negotiated_deal',
        help_text="The order created from this deal (null until buyer places order)"
    )

    class Meta:
        verbose_name = "Negotiated Deal"
        verbose_name_plural = "Negotiated Deals"
        ordering = ['-accepted_at']

    def __str__(self):
        return (
            f"Deal: {self.thread.buyer.username} ↔ {self.thread.seller.username} | "
            f"{self.thread.product.name} @ UGX {self.agreed_price}/{self.thread.product.unit}"
        )

