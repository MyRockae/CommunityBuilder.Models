from datetime import timedelta

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def _backfill_slot_sessions(apps, schema_editor):
    StorePurchase = apps.get_model('community_store', 'StorePurchase')
    StoreSlotSession = apps.get_model('community_store', 'StoreSlotSession')
    StoreBookableMeetingSettings = apps.get_model('community_store', 'StoreBookableMeetingSettings')

    settings_by_product = {
        row.store_product_id: row
        for row in StoreBookableMeetingSettings.objects.all()
    }

    seen = set()
    qs = StorePurchase.objects.filter(booked_slot_start_utc__isnull=False).only(
        'id', 'product_id', 'booked_slot_start_utc',
    )
    for row in qs.iterator(chunk_size=500):
        start = row.booked_slot_start_utc
        key = (row.product_id, start)
        if key in seen:
            continue
        seen.add(key)
        if StoreSlotSession.objects.filter(store_product_id=row.product_id, slot_start_utc=start).exists():
            continue
        cfg = settings_by_product.get(row.product_id)
        duration = int(getattr(cfg, 'duration_minutes', None) or 30)
        source = (getattr(cfg, 'room_source', None) or '') if cfg else ''
        provider = source if source in ('google_meet', 'zoom') else ''
        max_att = int(getattr(cfg, 'max_attendees', None) or 1) if cfg else 1
        session = StoreSlotSession.objects.create(
            store_product_id=row.product_id,
            slot_start_utc=start,
            slot_end_utc=start + timedelta(minutes=duration),
            conference_provider=provider,
            max_attendees_snapshot=max_att,
            conference_status='none',
        )
        session.ics_uid = f'store-slot-{session.id}@rockae.com'
        session.save(update_fields=['ics_uid'])

    for row in StorePurchase.objects.filter(booked_slot_start_utc__isnull=False, slot_session_id__isnull=True):
        session = StoreSlotSession.objects.filter(
            store_product_id=row.product_id,
            slot_start_utc=row.booked_slot_start_utc,
        ).first()
        if session:
            row.slot_session_id = session.id
            row.save(update_fields=['slot_session'])


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0011_storepurchase_require_buyer_user'),
        ('community', '0030_community_bunny_collection_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityConferenceConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('google_meet', 'Google Meet'), ('zoom', 'Zoom')], max_length=20)),
                ('account_email', models.EmailField(blank=True, default='', max_length=254)),
                ('provider_user_id', models.CharField(blank=True, default='', max_length=255)),
                ('refresh_token_encrypted', models.TextField(blank=True, default='')),
                ('access_token_encrypted', models.TextField(blank=True, default='')),
                ('access_token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('scopes', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('revoked', 'Revoked')], db_index=True, default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conference_connections', to='community.community')),
                ('connected_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='community_conference_connections', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Community conference connection',
                'verbose_name_plural': 'Community conference connections',
                'db_table': 'CommunityConferenceConnection',
            },
        ),
        migrations.AddConstraint(
            model_name='communityconferenceconnection',
            constraint=models.UniqueConstraint(fields=('community', 'provider'), name='communityconference_unique_community_provider'),
        ),
        migrations.AddField(
            model_name='storebookablemeetingsettings',
            name='max_attendees',
            field=models.PositiveIntegerField(default=1, help_text='People per session. 1 = exclusive, N = capped group, 0 = unlimited.'),
        ),
        migrations.AddField(
            model_name='storebookablemeetingsettings',
            name='room_source',
            field=models.CharField(
                choices=[
                    ('manual', 'Provide URL manually'),
                    ('google_meet', 'Google Meet'),
                    ('zoom', 'Zoom'),
                ],
                default='manual',
                help_text='manual (paste URL), google_meet, or zoom',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='storebookablemeetingsettings',
            name='manual_join_url',
            field=models.URLField(
                blank=True,
                help_text='Join URL reused for every slot when room_source is manual',
                null=True,
            ),
        ),
        migrations.CreateModel(
            name='StoreSlotSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_start_utc', models.DateTimeField(db_index=True)),
                ('slot_end_utc', models.DateTimeField()),
                ('conference_provider', models.CharField(blank=True, choices=[('google_meet', 'Google Meet'), ('zoom', 'Zoom')], default='', max_length=20)),
                ('max_attendees_snapshot', models.PositiveIntegerField(default=1)),
                ('join_url', models.URLField(blank=True, default='')),
                ('host_start_url', models.URLField(blank=True, default='')),
                ('provider_meeting_id', models.CharField(blank=True, default='', max_length=255)),
                ('ics_uid', models.CharField(blank=True, default='', max_length=255)),
                ('ics_sequence', models.PositiveIntegerField(default=0)),
                ('conference_status', models.CharField(choices=[('none', 'Not provisioned'), ('ready', 'Ready'), ('failed', 'Failed')], db_index=True, default='none', max_length=20)),
                ('conference_error', models.TextField(blank=True, default='')),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slot_sessions', to='community_store.storeproduct')),
            ],
            options={
                'verbose_name': 'Store slot session',
                'verbose_name_plural': 'Store slot sessions',
                'db_table': 'StoreSlotSession',
            },
        ),
        migrations.AddConstraint(
            model_name='storeslotsession',
            constraint=models.UniqueConstraint(fields=('store_product', 'slot_start_utc'), name='storeslotsession_unique_product_start'),
        ),
        migrations.AddIndex(
            model_name='storeslotsession',
            index=models.Index(fields=['store_product', 'slot_start_utc'], name='StoreSlotSe_store_p_idx'),
        ),
        migrations.AddIndex(
            model_name='storeslotsession',
            index=models.Index(fields=['conference_status'], name='StoreSlotSe_confere_idx'),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='buyer_name',
            field=models.CharField(blank=True, default='', help_text='Display name collected at checkout', max_length=255),
        ),
        migrations.AlterField(
            model_name='storepurchase',
            name='buyer_user',
            field=models.ForeignKey(blank=True, help_text='Logged-in buyer; null for guest checkout', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='store_purchases', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='slot_session',
            field=models.ForeignKey(blank=True, help_text='Bookable occurrence this purchase reserved', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchases', to='community_store.storeslotsession'),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='checkout_expires_at',
            field=models.DateTimeField(blank=True, help_text='When a pending meeting checkout stops occupying a seat', null=True),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='buyer_fulfillment_emailed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='host_notified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='calendar_invited_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['slot_session'], name='StorePurcha_slot_se_idx'),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['checkout_expires_at'], name='StorePurcha_checkou_idx'),
        ),
        migrations.RemoveConstraint(
            model_name='storeproductslothold',
            name='store_slothold_unique_pending_slot',
        ),
        migrations.AddConstraint(
            model_name='storeproductslothold',
            constraint=models.UniqueConstraint(
                condition=models.Q(status='pending'),
                fields=('store_product', 'slot_start_utc', 'buyer_user'),
                name='store_slothold_unique_pending_slot_buyer',
            ),
        ),
        migrations.CreateModel(
            name='StoreGuestEmailChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('buyer_name', models.CharField(blank=True, default='', max_length=255)),
                ('code_hash', models.CharField(max_length=128)),
                ('expires_at', models.DateTimeField()),
                ('attempt_count', models.PositiveSmallIntegerField(default=0)),
                ('consumed_at', models.DateTimeField(blank=True, null=True)),
                ('last_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='store_guest_email_challenges', to='community.community')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guest_email_challenges', to='community_store.storeproduct')),
            ],
            options={
                'verbose_name': 'Store guest email challenge',
                'verbose_name_plural': 'Store guest email challenges',
                'db_table': 'StoreGuestEmailChallenge',
            },
        ),
        migrations.AddIndex(
            model_name='storeguestemailchallenge',
            index=models.Index(fields=['email', 'expires_at'], name='StoreGuestE_email_ex_idx'),
        ),
        migrations.RunPython(_backfill_slot_sessions, migrations.RunPython.noop),
    ]
