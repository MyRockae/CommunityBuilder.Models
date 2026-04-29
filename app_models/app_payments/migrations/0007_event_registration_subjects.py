import django
import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


def _payment_checkoutsession_subject_check_constraint():
    q = (
        Q(
            app_subscription__isnull=False,
            community_member_subscription__isnull=True,
            store_purchase__isnull=True,
            event_registration__isnull=True,
        )
        | Q(
            app_subscription__isnull=True,
            community_member_subscription__isnull=False,
            store_purchase__isnull=True,
            event_registration__isnull=True,
        )
        | Q(
            app_subscription__isnull=True,
            community_member_subscription__isnull=True,
            store_purchase__isnull=False,
            event_registration__isnull=True,
        )
        | Q(
            app_subscription__isnull=True,
            community_member_subscription__isnull=True,
            store_purchase__isnull=True,
            event_registration__isnull=False,
        )
    )
    name = "paymentcheckoutsession_exactly_one_subject"
    if django.VERSION >= (5, 2):
        return models.CheckConstraint(condition=q, name=name)
    return models.CheckConstraint(check=q, name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("community_event", "0001_initial"),
        ("app_payments", "0006_rename_paymentcheck_user_stat_exp_idx_paymentchec_user_id_3cb72e_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentcheckoutsession",
            name="event_registration",
            field=models.ForeignKey(
                blank=True,
                help_text="Set when session_kind is event_registration",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_checkout_sessions",
                to="community_event.eventregistration",
            ),
        ),
        migrations.AddField(
            model_name="paymenttransaction",
            name="event_registration",
            field=models.ForeignKey(
                blank=True,
                help_text="Event registration (if transaction_type is event_registration)",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_transactions",
                to="community_event.eventregistration",
            ),
        ),
        migrations.AlterField(
            model_name="paymentcheckoutsession",
            name="session_kind",
            field=models.CharField(
                choices=[
                    ("app_subscription", "App Subscription"),
                    ("community_member_subscription", "Community Member Subscription"),
                    ("store_purchase", "Store Product Purchase"),
                    ("event_registration", "Event Registration"),
                ],
                help_text="Which subject FK is populated — same vocabulary as PaymentTransaction.transaction_type",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="paymenttransaction",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("app_subscription", "App Subscription"),
                    ("community_member_subscription", "Community Member Subscription"),
                    ("store_purchase", "Store Product Purchase"),
                    ("event_registration", "Event Registration"),
                ],
                help_text="Type of transaction",
                max_length=50,
            ),
        ),
        migrations.AddIndex(
            model_name="paymenttransaction",
            index=models.Index(fields=["event_registration", "status"], name="PaymentTran_event_r_6194a6_idx"),
        ),
        migrations.RemoveConstraint(
            model_name="paymentcheckoutsession",
            name="paymentcheckoutsession_exactly_one_subject",
        ),
        migrations.AddConstraint(
            model_name="paymentcheckoutsession",
            constraint=_payment_checkoutsession_subject_check_constraint(),
        ),
    ]
