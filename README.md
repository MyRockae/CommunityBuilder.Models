# CommunityBuilder.Models

Shared Django models package for the CommunityBuilder platform. Use this repo as a dependency in your API (or other Django project) so all services share the same model and migration definitions.

## Overview

- **Python:** 3.8+
- **Dependencies:** Django ≥ 4.0, djangorestframework  
- **Package layout:** All models live under the `app_models` package. Each app is a subpackage (e.g. `app_models.community`, `app_models.account`).

## Apps and domains

| App | Description |
|-----|-------------|
| `account` | User, UserRole (custom auth; email as username) |
| `user_profile` | UserProfile (name, bio, interests, avatar, etc.) |
| `shared` | Tag, custom API exceptions |
| `community` | Community, CommunityMember, CommunityLike, CommunityView, CommunityGroup, CommunityGroupAccess, CommunityBadgeDefinition, CommunityMemberBadge |
| `community_classroom` | Classroom (courses; payment plans, is_published, certificates) |
| `community_classroom_content` | ClassroomContent, ClassroomAttachment, ClassroomContentCompletion, ClassroomCertificate |
| `community_forum` | Forum, Post, PostAttachment, PostLike |
| `community_blog` | CommunityBlogPost, CommunityBlogPostReply |
| `blog` | BlogPost (platform-wide) |
| `community_resource` | Resource, ResourceContent (file folders + files) |
| `community_quiz` | Quiz, QuizGenerationJob, QuizSubmission |
| `community_polls` | Poll, PollOption, PollVote |
| `community_meetings` | Meeting, MeetingSeries (recurring template) |
| `community_chat` | Conversation, ConversationParticipant, Message |
| `community_wheel` | Wheel, WheelParticipant, WheelHandoff, WheelHandoffAttachment (e.g. ajo/savings circles) |
| `community_publicfeeds` | PublicFeed, PublicFeedsAttachment, PublicFeedsLike |
| `community_feedback` | CommunityFeedback (ratings + message per community) |
| `community_leave_reason` | CommunityLeaveReason |
| `community_abuse_report` | CommunityAbuseReport (user reports/flagging of communities) |
| `badges` | BadgeDefinition, UserBadge (app-level badges) |
| `app_payments` | `PaymentGateway`, `PaymentTransaction`, `CreatorPayoutAccount` |
| `app_subscription` | `AppSubscriptionTier`, `AppSubscriptionTierPrice`, `AppSubscription`, `CommunityMemberSubscription` |
| `storage_usage` | `StorageUsage` (per-owner file bytes for tier limits) |

## Installation

Install the package (e.g. from Git), then add every `app_models.*` app you use to your project’s `INSTALLED_APPS`. See [INSTALL.md](INSTALL.md) for Git install and usage examples.

**Order:** declare **`app_models.app_payments` before `app_models.app_subscription`** (subscription models import `PaymentGateway` from `app_payments`). Include **`app_models.storage_usage`** if you use `StorageUsage`.

**Imports (after the split):** `PaymentTransaction`, `CreatorPayoutAccount`, and `PaymentGateway` → `app_models.app_payments.models`. `StorageUsage` → `app_models.storage_usage.models`.

## Usage

After installation, import models from the `app_models` namespace:

```python
from app_models.account.models import User
from app_models.community.models import Community, CommunityMember
from app_models.community_classroom.models import Classroom
# etc.
```

Run migrations from your Django project so the database schema stays in sync with this package.

### CommunityGroup rename (`community.0011`)

Apply migrations with a **full** `python manage.py migrate`, not `migrate community` alone. If `community.0011` is recorded while follow-up migrations are not, Django can fail on startup with *lazy reference to `community.paymentplan`* because `PaymentPlan` no longer exists in migration state.

**Recovery (PostgreSQL):** if the DB already matches the renamed schema (tables/columns from `0011` and the M2M state-only migrations) but `django_migrations` is missing rows, insert the missing names so state matches reality, then run `migrate` again:

```sql
INSERT INTO django_migrations (app, name, applied)
SELECT v.app, v.name, NOW() FROM (VALUES
  ('community_polls', '0002_alter_poll_payment_plans'),
  ('community_quiz', '0002_alter_quiz_payment_plans'),
  ('community_resource', '0006_alter_resource_payment_plans'),
  ('community_forum', '0003_alter_forum_payment_plans'),
  ('community_classroom', '0003_alter_classroom_payment_plans'),
  ('community_meetings', '0003_alter_meeting_payment_plans'),
  ('app_subscription', '0003_rename_community_group_fields')
) AS v(app, name)
WHERE NOT EXISTS (
  SELECT 1 FROM django_migrations d WHERE d.app = v.app AND d.name = v.name
);
```

Skip any row for an app/migration you have not actually applied yet (schema mismatch). If the database was **not** fully migrated through `0011`, roll back with a restore or reverse the schema manually instead of inserting rows.
