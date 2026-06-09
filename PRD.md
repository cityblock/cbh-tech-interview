# System Design Interview — After Hours Support PRD

> This is the candidate-facing prompt for the System Design Interview — the single
> source of truth shared with candidates. It deliberately contains no interviewer
> notes, answer key, or scoring.
>
> Source: [Notion — System Design Interview — After Hours Support PRD](https://app.notion.com/p/560299412c224f4782829d26830f85fa)

# After hours support for Messaging

## Why this matters

We want to automatically handle patient messages that arrive when a user is _off the
clock_ — for example, sending an after-hours auto-response instead of leaving a patient
waiting on someone who isn't working. To do any of that, the system first needs a
reliable answer to a deceptively simple question: **when is a given user actually
available to be contacted?** This exercise is about modeling that availability well; the
after-hours auto-response is the motivating use case, and the stretch goal at the end.

## Scenario

Our company provides Virtual Urgent Care, giving patients a 24/7 phone number to call and
be immediately connected with a nurse. To manage that 24/7 coverage, we have an internal
web app where users (nurses and scheduling managers) can manage their own availability and
view the availability of other users.

## Problem

Our goal is to store in our database when a user is available to be contacted. In the
past, all we needed to know was which days a user worked (or was available) throughout the
week, so we stored this in our User table. We assumed that on those days they worked
9am–5pm Eastern.

As the company has grown, we've shifted to accommodate people in different locales and with
non-default working schedules. What changes are needed to support this?

> 🧭 Nothing here is sacred. The current data model and the 9am–5pm Eastern assumption are
> a _legacy starting point_, not a spec to implement — question the use cases, the schema,
> and the feature spec as you see fit, and note any changes in your proposal.

## Current state

**User table**

```
id           <UUID>
firstName    <string>
lastName     <string>
phoneNumber  <phoneNumber>
availability <jsonb> { availableDays: [string] }
```

## Prompt: write an engineering design document outlining your proposed solution

The proposal should include:

- New / updated data models, including validation
- A pros / cons list of the trade-offs made for this proposal
- Details on how we will roll out the feature

**Requirements:**

1. **Milestone 1 — track basic availability.** Think "Working hours" from Google Calendar
   (don't over-index on this; it's just a sample visual). Example: set up your usual
   working hours.
2. **Milestone 2 — track one-off availability.** Deviations from the normal schedule in
   Milestone 1 — think doctor's appointments, vacations, one-time shifted hours, etc.
