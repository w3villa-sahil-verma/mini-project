# Image Gallery

## Backend configuration

Copy the root `.env.example` to `<project-root>/.env`. Backend configuration
is loaded through `src/core/settings.py`; process environment variables override
values from that file. Blank optional SMTP values stay unset, and blank
numeric/boolean mail settings use their defaults. Keep secrets in the ignored
root `.env` file and never commit it.

For Render, use the repository root as the service root directory,
`pip install -r requirements.txt` as the build command, and
`uvicorn src.Application:app --host 0.0.0.0 --port $PORT` as the start command.
Configure production secrets and service URLs as Render environment variables.

## Razorpay payments

Set the backend `ROZAR_PAY_API_KEY` and `ROZAR_PAY_SECRET` in the root `.env`
file (or Render environment variables). Use the test credentials from the
Razorpay dashboard while developing. The API key ID is public; the secret must
never be exposed to the frontend or committed. Configure the public checkout
key separately in the frontend's Vite environment.

The authenticated `POST /api/v1/payments/checkout` endpoint creates an order
using the selected active plan's server-side price. Free plans are activated
without checkout. For paid plans, the frontend opens Razorpay Checkout and
submits its callback to `POST /api/v1/payments/verify`; the backend verifies
the signature before activating or scheduling the membership. A new paid plan
is scheduled after any existing active or scheduled membership. The signed-in
user's memberships can be read from `GET /api/v1/payments/subscriptions/me`.

## Google and Facebook sign-in

Set the provider credentials and callback URLs in the root `.env` file (see
the root `.env.example`). In the Google Cloud and Meta developer consoles, register
the corresponding callback URLs exactly:

```text
http://localhost:8000/api/v1/auth/oauth/google/callback
http://localhost:8000/api/v1/auth/oauth/facebook/callback
```

The login and registration pages send users to
`GET /api/v1/auth/oauth/{google|facebook}`. The backend stores a short-lived,
HTTP-only OAuth state cookie, exchanges the authorization code server-side,
and creates or finds a user before setting the normal HTTP-only
`access_token` cookie. New provider emails create a regular user account.
Google email must be provider-verified. When a provider reports the same email
as an existing account, its provider identity is linked to that account;
Facebook sign-in requires the provider to return an email. The callback
redirects successful users to the frontend home page. Use
`OAUTH_COOKIE_SECURE=true` with HTTPS in production; the example disables the
secure-cookie flag for local HTTP development.

## Admin dashboard

The admin dashboard reads its overview from
`GET /api/v1/admin/dashboard`. The admin-only endpoint returns plan and user
totals, active subscriptions, monthly user-registration and subscription
counts for the last 12 months, recent users, plan details, and upcoming
subscription expirations.

The admin user list at `/admin/users` uses
`GET /api/v1/admin/users?page=1&page_size=20&search=...&role=USER&status=active`.
Search matches a user's name, email, phone, or ID. Role and account status can
be filtered independently, and responses include total counts and pagination
metadata. User names come from the optional user profile; accounts without a
profile name are shown as not provided.

The application checks subscription expirations once per minute and marks
subscriptions with an elapsed `expires_at` as `EXPIRED`. Plans remain available
in the shared plan catalog; expiration applies to the individual user's
subscription. The profile reports whether the user currently has premium
membership access, and the admin dashboard includes expired subscription
counts and recent expirations.

## Profile images with Storj

Configure these values in the root `.env` (or as backend environment variables):

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
header. For public image delivery, set `STORJ_PUBLIC_BASE_URL` to the Storj Linksharing
prefix including the access grant, for example
`https://link.storjshare.io/raw/<ACCESS_GRANT>`. The bucket and object key are
appended by the backend. A bare `/raw` URL is not sufficient and falls back to
a one-hour signed GET URL. Leave it empty for private buckets; the backend then
generates a one-hour signed GET URL when returning the profile.

## Gallery

Anyone can browse `/gallary`. Free images are visible to all visitors;
premium images are unlocked only for a valid signed-in user with an active
subscription and remain unlocked only through that subscription's expiry.
Locked premium tiles use a blurred/locked placeholder without returning the
image URL. Admins manage the gallery at `/admin/gallery`, where images can be
uploaded in bulk, marked free or premium, paginated, or deleted individually
and in bulk. Gallery uploads use the same Storj S3-compatible settings and
5 MB image limits as profile images.
