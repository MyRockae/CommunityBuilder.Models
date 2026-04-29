import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("community", "0022_rename_cgjoinreq_grp_status_idx_communitygr_communi_639875_idx_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app_payments", "0006_rename_paymentcheck_user_stat_exp_idx_paymentchec_user_id_3cb72e_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommunityEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Event title", max_length=255)),
                ("description", models.TextField(blank=True, help_text="Event description", null=True)),
                ("starts_at", models.DateTimeField(help_text="Event start datetime")),
                ("ends_at", models.DateTimeField(help_text="Event end datetime")),
                ("venue_type", models.CharField(choices=[("remote", "Remote"), ("physical", "Physical")], default="remote", max_length=20)),
                ("remote_join_url", models.URLField(blank=True, help_text="Remote meeting URL", null=True)),
                ("address_line_1", models.CharField(blank=True, max_length=255, null=True)),
                ("address_line_2", models.CharField(blank=True, max_length=255, null=True)),
                ("city", models.CharField(blank=True, max_length=120, null=True)),
                ("state_region", models.CharField(blank=True, max_length=120, null=True)),
                ("postal_code", models.CharField(blank=True, max_length=32, null=True)),
                ("country_code", models.CharField(blank=True, max_length=2, null=True)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("banner_url", models.URLField(blank=True, help_text="Optional event banner", null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "community",
                    models.ForeignKey(
                        help_text="Community that owns this event",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="community.community",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_community_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Community event",
                "verbose_name_plural": "Community events",
                "db_table": "CommunityEvent",
                "ordering": ["-starts_at", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="EventRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending payment"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("amount_paid", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("stripe_payment_intent_id", models.CharField(blank=True, max_length=255, null=True)),
                ("stripe_checkout_session_id", models.CharField(blank=True, max_length=255, null=True)),
                ("stripe_customer_id", models.CharField(blank=True, max_length=255, null=True)),
                ("billing_country", models.CharField(blank=True, max_length=2, null=True)),
                ("payment_gateway", models.CharField(blank=True, choices=[("stripe", "Stripe"), ("paystack", "Paystack")], max_length=20, null=True)),
                ("paystack_customer_code", models.CharField(blank=True, max_length=255, null=True)),
                ("paystack_transaction_reference", models.CharField(blank=True, max_length=255, null=True)),
                ("purchased_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "attendee_user",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="event_registrations", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "event",
                    models.ForeignKey(
                        help_text="Event being registered for",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registrations",
                        to="community_event.communityevent",
                    ),
                ),
            ],
            options={
                "verbose_name": "Event registration",
                "verbose_name_plural": "Event registrations",
                "db_table": "EventRegistration",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CommunityEventPrice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("currency", models.CharField(help_text="ISO 4217 code (e.g. USD, NGN)", max_length=3)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "community_event",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prices", to="community_event.communityevent"),
                ),
            ],
            options={
                "verbose_name": "Community event price",
                "verbose_name_plural": "Community event prices",
                "db_table": "CommunityEventPrice",
            },
        ),
        migrations.AddIndex(
            model_name="communityevent",
            index=models.Index(fields=["community", "starts_at"], name="CommunityEv_communi_b6c73a_idx"),
        ),
        migrations.AddIndex(
            model_name="communityevent",
            index=models.Index(fields=["community", "is_active"], name="CommunityEv_communi_80f0ee_idx"),
        ),
        migrations.AddConstraint(
            model_name="communityeventprice",
            constraint=models.UniqueConstraint(fields=("community_event", "currency"), name="communityeventprice_unique_event_currency"),
        ),
        migrations.AddIndex(
            model_name="communityeventprice",
            index=models.Index(fields=["community_event", "currency"], name="CommunityEv_communi_bb9207_idx"),
        ),
        migrations.AddIndex(
            model_name="eventregistration",
            index=models.Index(fields=["event", "status"], name="EventRegist_event_i_b7ac98_idx"),
        ),
        migrations.AddIndex(
            model_name="eventregistration",
            index=models.Index(fields=["attendee_user", "status"], name="EventRegist_attende_bda489_idx"),
        ),
        migrations.AddIndex(
            model_name="eventregistration",
            index=models.Index(fields=["stripe_payment_intent_id"], name="EventRegist_stripe__70337d_idx"),
        ),
        migrations.AddIndex(
            model_name="eventregistration",
            index=models.Index(fields=["paystack_transaction_reference"], name="EventRegist_paystac_82e095_idx"),
        ),
        migrations.AddIndex(
            model_name="eventregistration",
            index=models.Index(fields=["payment_gateway"], name="EventRegist_payment_67ff2d_idx"),
        ),
        migrations.AddConstraint(
            model_name="eventregistration",
            constraint=models.UniqueConstraint(
                condition=models.Q(status="completed"),
                fields=("event", "attendee_user"),
                name="eventregistration_unique_completed_attendee_per_event",
            ),
        ),
    ]
