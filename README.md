# ABC GYM

Best GYM of Kanpur

| Feature                    | 🆓 Free | 🥈 Silver |    🥇 Gold   |
| -------------------------- | :-----: | :-------: | :----------: |
| Gym floor access           |    ✅    |     ✅     |       ✅      |
| Basic workout plans        |    ✅    |     ✅     |       ✅      |
| Exercise library           | Limited |    Full   |     Full     |
| Workout tracking           |    ❌    |     ✅     |       ✅      |
| Progress tracking          |    ❌    |     ✅     |       ✅      |
| Body measurement tracking  |    ❌    |     ✅     |       ✅      |
| Personalized workout plan  |    ❌    |     ❌     |       ✅      |
| AI workout recommendations |    ❌    |     ❌     |       ✅      |
| Trainer consultation       |    ❌    | 1 session |  2 sessions  |
| Group classes              |    ❌    |     ✅     |       ✅      |
| Premium classes            |    ❌    |     ❌     |       ✅      |
| Diet/nutrition guidance    |  Basic  |  Standard | Personalized |
| Workout history            |    ❌    |  30 days  |   Unlimited  |
| Advanced analytics         |    ❌    |     ❌     |       ✅      |
| Personal trainer priority  |    ❌    |     ❌     |       ✅      |
| Guest pass                 |    ❌    |     ❌     |    1 guest   |
| Exclusive offers           |    ❌    |     ✅     |       ✅      |
| Priority support           |    ❌    |     ❌     |       ✅      |

## Razorpay payments

Set `ROZAR_PAY_API_KEY` in both `frontend/.env` and `src/.env`, and set
`ROZAR_PAY_SECRET` only in `src/.env`. Use the test credentials from the
Razorpay dashboard while developing. The API key ID is public; the secret must
never be exposed to the frontend or committed.

The authenticated `POST /api/v1/payments/checkout` endpoint creates an order
using the selected active plan's server-side price. Free plans are activated
without checkout. For paid plans, the frontend opens Razorpay Checkout and
submits its callback to `POST /api/v1/payments/verify`; the backend verifies
the signature before activating or scheduling the membership. A new paid plan
is scheduled after any existing active or scheduled membership. The signed-in
user's memberships can be read from `GET /api/v1/payments/subscriptions/me`.

## Admin dashboard

The admin dashboard reads its overview from
`GET /api/v1/admin/dashboard`. The admin-only endpoint returns plan and user
totals, active subscriptions, monthly user-registration and subscription
counts for the last 12 months, recent users, plan details, and upcoming
subscription expirations.

The application checks subscription expirations once per minute and marks
subscriptions with an elapsed `expires_at` as `EXPIRED`. Plans remain available
in the shared plan catalog; expiration applies to the individual user's
subscription. The profile reports whether the user currently has premium
membership access, and the admin dashboard includes expired subscription
counts and recent expirations.
