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
| `community` | Community, CommunityMember, CommunityLike, CommunityView, PaymentPlan, UserPaymentPlan, CommunityBadgeDefinition, CommunityMemberBadge |
| `community_classroom` | Classroom (courses; payment plans, is_published, certificates) |
| `community_classroom_content` | ClassroomContent, ClassroomAttachment, ClassroomContentCompletion, ClassroomCertificate |
| `community_forum` | Forum, Post, PostAttachment, PostLike |
| `community_blog` | CommunityBlogPost, CommunityBlogPostReply |
| `blog` | BlogPost (platform-wide) |
| `community_resource` | Resource, ResourceContent (file folders + files) |
| `community_quiz` | Quiz, QuizGenerationJob, QuizSubmission |
| `community_polls` | Poll, PollOption, PollVote |
| `community_meetings` | Meeting |
| `community_chat` | Conversation, ConversationParticipant, Message |
| `community_wheel` | Wheel, WheelParticipant, WheelHandoff, WheelHandoffAttachment (e.g. ajo/savings circles) |
| `community_publicfeeds` | PublicFeed, PublicFeedsAttachment, PublicFeedsLike |
| `community_feedback` | CommunityFeedback (ratings + message per community) |
| `community_leave_reason` | CommunityLeaveReason |
| `community_abuse_report` | CommunityAbuseReport (user reports/flagging of communities) |
| `badges` | BadgeDefinition, UserBadge (app-level badges) |
| `app_subscription` | AppSubscriptionTier, AppSubscription, StorageUsage, CommunityMemberSubscription, PaymentTransaction |

## Installation

Install the package (e.g. from Git), then add every `app_models.*` app you use to your project’s `INSTALLED_APPS`. See [INSTALL.md](INSTALL.md) for Git install and usage examples.

## Usage

After installation, import models from the `app_models` namespace:

```python
from app_models.account.models import User
from app_models.community.models import Community, CommunityMember
from app_models.community_classroom.models import Classroom
# etc.
```

Run migrations from your Django project so the database schema stays in sync with this package.
