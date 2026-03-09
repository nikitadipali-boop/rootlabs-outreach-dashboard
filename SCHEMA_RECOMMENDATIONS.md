# Airtable Schema Recommendations - Outreach Intelligence Table

## Context

This document captures all recommended schema changes to the Outreach Intelligence table.
Apply these before building the reply engine and follow-up automation.
Written: March 9, 2026.

---

## EXISTING FIELDS TO MODIFY

### 1. `thread_status` (Single Select - add new options)

Currently missing:

| New Option | When to Use |
|------------|-------------|
| `abandoned` | Followup 3 was sent, no response from creator after 2 days |
| `deal_closed` | Creator agreed, deal confirmed |
| `not_interested` | Creator explicitly declined or unsubscribed |
| `paused` | Conversation on hold (e.g. creator said "reach me in 2 weeks") |

---

## NEW FIELDS TO ADD

### 2. `creator_comms_preference` (Single Select)

Tracks how the creator wants to be contacted. Critical for the reply engine to know never to ask for WhatsApp from email-only creators.

| Option | Meaning |
|--------|---------|
| `email_only` | Creator explicitly declined phone/WhatsApp - keep all comms on email |
| `whatsapp_preferred` | Creator gave WhatsApp number and prefers that channel |
| `email_preferred` | Creator hasn't declined WhatsApp but prefers email |

**Who updates it:** Creator relations team, or auto-set by reply engine based on thread content.
**Priority:** High - needed before reply engine goes live. 34 creators already identified as `email_only`.

---

### 3. `creator_username` (Single Line Text)

The TikTok/Instagram handle of the creator (e.g. `@alohaitzkiana`).
Currently this lives buried inside the email body of the first outbound message.
Having it as a standalone field enables:
- Sorting and filtering by creator handle
- Cross-referencing with Apollo contact records
- Display in dashboards without parsing email text

**Who updates it:** Auto-populated when thread is first created (from Apollo contact data).

---

### 4. `creator_name` (Single Line Text)

The creator's real name, separate from their handle.
Currently only extractable by parsing the "From:" header of inbound emails.

**Who updates it:** Auto-populated or manually by creator relations team.

---

### 5. `reply_sent_at` (Date/Time)

Timestamp of when the first reply (`done_reply`) was sent.
Currently missing - `last_message_date` gets overwritten by every subsequent message,
so we lose the exact moment the first reply went out.
This is essential for calculating the 2-day cadence accurately.

**Who updates it:** Auto-set by the reply engine when marking `action_status = done_reply`.

---

### 6. `followup_1_sent_at` (Date/Time)

Timestamp of when follow-up 1 was sent.
Required to know when the 2-day window for follow-up 2 opens.

**Who updates it:** Auto-set by the follow-up engine when marking `action_status = done_followup_1`.

---

### 7. `followup_2_sent_at` (Date/Time)

Timestamp of when follow-up 2 was sent.
Required to know when the 2-day window for follow-up 3 opens.

**Who updates it:** Auto-set by the follow-up engine when marking `action_status = done_followup_2`.

---

### 8. `followup_3_sent_at` (Date/Time)

Timestamp of when follow-up 3 was sent.
After 2 days with no response, thread moves to `abandoned`.

**Who updates it:** Auto-set by the follow-up engine when marking `action_status = done_followup_3`.

---

### 9. `next_action_due_at` (Date/Time)

Computed field: the exact datetime when the next action is due.
Calculated as: last action timestamp + 2 days.
Allows the system to pull a daily queue of "what needs to go out today."

**Who updates it:** Auto-recalculated every time an action status changes.

---

### 10. `assigned_to` (Single Select or Collaborator)

Which team member is responsible for this thread.
Enables workload distribution across the creator relations team.

| Option | Meaning |
|--------|---------|
| `may_k` | Assigned to May K |
| `mayank` | Assigned to Mayank |
| `team` | Unassigned / shared queue |

**Who updates it:** Team lead or auto-assigned based on `rootlabs_email` inbox.

---

### 11. `deal_value` (Currency)

Expected retainer or deal value if the creator converts.
Enables prioritisation - higher value deals get faster follow-up.

**Who updates it:** Creator relations team once deal terms are discussed.

---

### 12. `creator_follower_bucket` (Single Select)

Size of the creator's audience. Useful for prioritising outreach queue.

| Option |
|--------|
| `nano` (under 10k) |
| `micro` (10k - 50k) |
| `mid` (50k - 250k) |
| `macro` (250k+) |

**Who updates it:** Auto-populated from Apollo custom fields on import.

---

### 13. `product` (Single Select)

Which RootLabs product this outreach is about.

| Option |
|--------|
| `MagAshwa` |
| `ShopDocs` |
| `HGR` (Hair Growth Roll-On) |
| `Other` |

**Who updates it:** Auto-set based on campaign name, or manually by team.

---

### 14. `notes` (Long Text)

Free-text field for the creator relations team to log context that doesn't fit elsewhere.
e.g. "Creator said she's travelling until March 20, follow up after."

**Who updates it:** Creator relations team manually.

---

### 15. `cta_type` (Single Select)

What kind of CTA the creator responded with - helps route next steps.

| Option | Meaning |
|--------|---------|
| `shared_phone` | Creator gave their WhatsApp/phone number |
| `email_only` | Creator declined phone, staying on email |
| `shared_rates` | Creator sent their rate card |
| `asked_for_details` | Creator wants more info before deciding |
| `requested_sample` | Creator asked for a product sample |
| `not_interested` | Creator declined |

**Who updates it:** Auto-classified by reply engine based on thread content.

---

## SUMMARY TABLE

| Field | Type | Priority | Auto or Manual |
|-------|------|----------|----------------|
| `thread_status` - add abandoned/deal_closed/not_interested/paused | Modify existing | High | Both |
| `creator_comms_preference` | Single Select | High | Both |
| `creator_username` | Single Line Text | High | Auto |
| `creator_name` | Single Line Text | Medium | Auto |
| `reply_sent_at` | Date/Time | High | Auto |
| `followup_1_sent_at` | Date/Time | High | Auto |
| `followup_2_sent_at` | Date/Time | High | Auto |
| `followup_3_sent_at` | Date/Time | High | Auto |
| `next_action_due_at` | Date/Time | High | Auto |
| `assigned_to` | Single Select | Medium | Manual |
| `deal_value` | Currency | Medium | Manual |
| `creator_follower_bucket` | Single Select | Low | Auto |
| `product` | Single Select | Medium | Auto |
| `notes` | Long Text | Medium | Manual |
| `cta_type` | Single Select | High | Auto |

---

## ORDER TO APPLY

1. Add `thread_status` options first (needed for abandoned status - 1 record waiting)
2. Add `creator_comms_preference` (34 records ready to be tagged)
3. Add all 4 timestamp fields (`reply_sent_at` through `followup_3_sent_at`) together
4. Add `next_action_due_at`
5. Add `cta_type`
6. Add `creator_username` and `creator_name`
7. Add remaining fields (`assigned_to`, `deal_value`, `product`, `notes`, `creator_follower_bucket`)
