# Airtable Visibility Tracker - Context File

## PURPOSE

This folder tracks all work related to the Airtable "Outreach Intelligence" base for RootLabs creator outreach. Pass this file to any Claude Code session to resume work without re-explaining the setup.

---

## ACCESS

- **Airtable Base:** Outreach Intelligence
- **Base ID:** appnhGIoeLSfLf9ah
- **Table ID:** tblwZwNeuZwtIavqj
- **View URL:** https://airtable.com/appnhGIoeLSfLf9ah/tblwZwNeuZwtIavqj/viwW6YEImr9YEwEUG
- **API Token:** pat0aSErPoCgOSR2B.4bde5ea5bcf124ac0680d144183be4baf5d158be0d19777e8a4fc7dd43037fa8
- **Access level:** Read + Write
- **Token owner user ID:** usrxWIwCIPCY3cwQH

---

## TABLE STRUCTURE

**Total records:** 1,483 (as of March 9, 2026)
Each record = one Gmail conversation thread between a RootLabs inbox and a creator/contact.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `gmail_thread_id` | Text | Links to the actual Gmail thread |
| `rootlabs_email` | Text | Which RootLabs inbox owns this thread |
| `creator_email` | Text | The creator/contact on the other end |
| `last_message_type` | Text | `inbound` (creator spoke last) or `outbound` (RootLabs spoke last) |
| `last_message_date` | DateTime | Timestamp of last message |
| `date_of_first_reply` | DateTime | When the creator first replied |
| `creator_last_message` | Long text | Creator's most recent message text |
| `rootlabs_last_message` | Long text | RootLabs' most recent message text |
| `complete_processed_thread` | Long text | Full conversation history as JSON array |
| `thread_status` | Text | Core routing field (see values below) |
| `action_status_auto` | Text | What the system auto-classified as done |
| `action_status_final` | Text | Confirmed final action taken |
| `action_status_manual` | Text | Manual override field |
| `cta_extracted_auto` | Text | Phone number/CTA auto-extracted from thread |
| `cta_extracted_final` | Text | Final confirmed CTA |
| `cta_closed_auto` | Checkbox | Whether CTA was fulfilled (auto) |
| `cta_closed_final` | Checkbox | Whether CTA was fulfilled (final) |
| `thread_reply_recommendations` | AI field | AI-generated reply suggestions (often empty/stale) |
| `thread_last_processed_at` | DateTime | When the record was last processed |
| `audit_log` | Long text | History of actions taken on the record |

### thread_status Values

| Value | Count | Meaning |
|-------|-------|---------|
| `needs_followup_1` | 728 | RootLabs replied, creator hasn't responded - needs follow-up 1 |
| `needs_reply` | 722 | Creator replied last - needs a response from RootLabs |
| `needs_followup_2` | 24 | Follow-up 1 sent, still no response - needs follow-up 2 |
| `needs_no_action` | 6 | Thread resolved or no action needed |
| `needs_followup_3` | 1 | Follow-up 2 sent, needs follow-up 3 |

### action_status Values (auto/final/manual)

| Value | Meaning |
|-------|---------|
| `done_reply` | A reply was sent to the creator |
| `done_followup_1` | Follow-up 1 was sent |
| `done_followup_2` | Follow-up 2 was sent |
| `done_followup_3` | Follow-up 3 was sent |
| `needs_no_action` | No action required |

### RootLabs Inboxes in Use

| Email | Record Count |
|-------|-------------|
| may_k@rootlabs.co | 534 |
| may.k@rootlabs.co | 175 |
| may@rootlabs.co | 150 |
| founder@rootlabs.co | 138 |
| may.kumar@rootlabs.co | 118 |
| mayank.kumar@rootlabs.co | 116 |
| mayank.k@rootlabs.co | 112 |
| ceo@rootlabs.co | 89 |
| mayk@rootlabs.co | 50 |

---

## CONVERSATION FLOW (inferred)

```
Creator replies to cold outreach
        |
        v
Thread enters Airtable --> thread_status: needs_reply
        |
        v
RootLabs sends a reply --> thread_status: needs_followup_1
                           action_status: done_reply
        |
        v
[No response from creator]
        |
        v
Follow-up 1 sent --> thread_status: needs_followup_2
                     action_status: done_followup_1
        |
        v
Follow-up 2 sent --> thread_status: needs_followup_3
                     action_status: done_followup_2
        |
        v
CTA extracted if creator shares phone number --> cta_extracted_final populated
```

---

## WORK COMPLETED (Session 1 - March 9, 2026)

### Non-Creator Cleanup

Identified and marked **333 records** as `action_status_manual = needs_no_action` because they are not creator conversations. Two categories:

**Category 1: Platform/SaaS/Tool automated emails**

| Domain | Count | Reason |
|--------|-------|--------|
| apollo.io + mail.apollo.io | 55 | Apollo platform emails |
| periskope.app | 42 | Messaging tool notifications |
| accounts.google.com | 36 | Google account notifications |
| mail.anthropic.com + email.claude.com | 19 | Anthropic/Claude |
| tello.com | 13 | Telecom service notifications |
| github.com | 11 | GitHub notifications |
| airtable.com + mail.airtable.com | 14 | Airtable notifications |
| engage.canva.com | 9 | Canva marketing emails |
| twelvelabs.io | 9 | SaaS platform |
| notify.railway.app + news.railway.app | 12 | Railway notifications |
| supabase.com | 8 | Supabase notifications |
| gamma.app | 6 | Gamma platform |
| apify.com | 6 | Apify platform |
| email.openai.com + tm.openai.com | 8 | OpenAI platform |
| mail.respond.io | 6 | Respond.io platform |
| qualfon.com | 6 | BPO/fulfillment pitch |
| reply.io | 5 | Reply.io sales tool |
| fyxer.com | 5 | AI email tool |
| mermaidchart.com + mermaid.ai | 7 | Mermaid Chart platform |
| team.twilio.com | 5 | Twilio notifications |
| news.railway.app | 5 | Railway newsletter |
| google.com | 4 | Google notifications |
| vidyard.com | 4 | Vidyard platform |
| superagent.com | 3 | Superagent platform |
| info.n8n.io | 3 | n8n automation platform |
| useloom.com | 3 | Loom platform |
| lemlist-news.com | 3 | Lemlist sales tool |
| amazon.com + amazonaws.com | 4 | Amazon/AWS notifications |
| notifications.hubspot.com | 2 | HubSpot notifications |
| mailchimp.com | 2 | Mailchimp notifications |
| send.zapier.com | 2 | Zapier notifications |
| discord.com | 2 | Discord notifications |
| reacherapp.com | 2 | Reacher email tool |
| klaviyo.com | 2 | Klaviyo marketing platform |
| boxbe.com | 2 | Boxbe email gating service |

**Category 2: Inbound B2B sales pitches TO RootLabs (not creators)**

| Domain | Count | What they pitched |
|--------|-------|-------------------|
| qualfon.com | 6 | BPO/fulfillment services |
| goshipcentrlpro.com | 2 | Shipping/fulfillment |
| ibramdawwa-gmbh.com | 2 | Video production |
| partnerssalesbytomorrowlead.info | 2 | Sales performance tools |
| huntdmfirm.info | 2 | Direct mail services |
| successgncapital.com | 1 | Business funding |
| evolvedcommerceflows.info | 1 | Wholesale commerce |
| meetapprovalprocessesdigital.com | 1 | Business capital |
| geniusecommerce-today.com | 1 | eCommerce services |
| checkaxisbrands.org | 1 | Amazon/brand strategy |

**Result after cleanup:**
- 333 non-creator records marked `needs_no_action`
- 5 already had that status
- ~1,145 remaining records are legitimate creator threads

---

## HOW TO QUERY THE TABLE

```python
import requests

TOKEN = "pat0aSErPoCgOSR2B.4bde5ea5bcf124ac0680d144183be4baf5d158be0d19777e8a4fc7dd43037fa8"
BASE_ID = "appnhGIoeLSfLf9ah"
TABLE_ID = "tblwZwNeuZwtIavqj"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Fetch all records (paginated)
all_records = []
offset = None
while True:
    params = {"pageSize": 100}
    if offset:
        params["offset"] = offset
    resp = requests.get(f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}", headers=HEADERS, params=params)
    data = resp.json()
    all_records.extend(data.get("records", []))
    offset = data.get("offset")
    if not offset:
        break
```

```python
# Update a batch of records (max 10 per request)
import requests

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def patch_batch(record_ids, field, value):
    payload = {
        "records": [{"id": rid, "fields": {field: value}} for rid in record_ids]
    }
    return requests.patch(f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}", headers=HEADERS, json=payload)
```

---

## NEXT STEPS (pending Tanya's flow instructions)

- Define triage logic for the ~1,145 remaining creator threads
- Determine what determines level/type of response needed per thread_status
- Automate reply recommendations or routing based on thread content
