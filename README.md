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

## Profile images with Storj

Configure these values in `src/.env` (or as backend environment variables):

```dotenv
STORJ_S3_ENDPOINT=https://gateway.storjshare.io
STORJ_ACCESS_KEY=your-storj-s3-access-key
STORJ_SECRET_KEY=your-storj-s3-secret-key
STORJ_BUCKET=your-bucket-name
STORJ_REGION=us-east-1
STORJ_PUBLIC_BASE_URL=
```

The authenticated `POST /api/v1/uploads/presign` endpoint accepts the file
name, MIME type, and size, stores that metadata in `image_assets`, and returns
a 60-second pre-signed PUT URL. The profile page uploads the image directly to
Storj, then calls `POST /api/v1/uploads/{image_id}/complete`. The backend
verifies the stored object's type and size before marking it ready and setting
it as the user's current profile image. JPEG, PNG, and WebP files up to 5 MB
are accepted.

Storj credentials never leave the backend. Configure the bucket's CORS policy
to allow the frontend origin to send `PUT` requests with the `Content-Type`
header. For public image delivery, set `STORJ_PUBLIC_BASE_URL` to the public
URL prefix for objects in the bucket. Leave it empty for private buckets; the
backend then generates a one-hour signed GET URL when returning the profile.
