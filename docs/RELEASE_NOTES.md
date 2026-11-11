# Project Release Notes

**Release:** Current repository snapshot (no version or release tag specified)  
**Date:** 2026-11-11

## Overview

Image Gallery is a photography browsing and membership application. Visitors can
explore public images, registered users can manage their profiles and purchase a
membership for premium access, and administrators can manage users, plans, and
gallery content.

The application includes a React, TypeScript, and Vite frontend and a FastAPI
backend built with SQLAlchemy and MySQL. Storj-compatible S3 object storage
hosts profile and gallery images.

## Features

### Public browsing and accounts

- Public home, pricing, and gallery pages, with `/gallery` as the canonical
  gallery route and `/gallary` supported as a legacy alias.
- Standard email-and-password registration and sign-in. Registration uses an
  emailed registration link.
- Google and Facebook OAuth sign-in. Provider identities can be linked to an
  existing account with the same email; Google email must be provider-verified
  and Facebook must return an email address.
- Password reset by email with a single-use link that expires after 30 minutes.
  Completing a reset invalidates existing refresh tokens.
- JWT-based authentication with HTTP-only access and refresh cookies. Refresh
  tokens are single-use, rotated, stored server-side, and revocable on logout;
  the frontend refreshes an expired session and retries the failed request.
- User and administrator roles with protected frontend routes and API access.

### Email notifications

- Email delivery follows a strategy pattern behind a shared notification
  service. Configure the provider to select either SMTP or Google Apps Script.
- Both providers support registration and password-reset email delivery.
- Google Apps Script requests use HTTPS and a configured shared secret. Provider
  errors are surfaced; the application does not silently fall back to another
  provider.

### Profiles and image storage

- Users can view and update profile information and upload a profile image.
- Profile and gallery uploads use short-lived, pre-signed Storj URLs, keeping
  storage credentials on the backend.
- The backend verifies uploaded object type and size before marking an asset
  ready. JPEG, PNG, and WebP images up to 5 MB are accepted.
- Profile images can be delivered through configured public Storj links or
  time-limited signed URLs.

### Gallery access

- Public, paginated gallery browsing with an infinite-scroll experience.
- Visitors receive low-resolution WebP previews; premium-image previews are
  watermarked. Original image objects remain private.
- Authenticated members can request original-resolution downloads through a
  protected endpoint. Silver access lasts one hour and Gold access lasts three
  hours after subscription activation, never extending beyond subscription
  expiry.
- Administrators can bulk-upload images, paginate the gallery, classify images
  as free or premium, and delete images individually or in bulk.
- Premium previews are regenerated when an image's premium classification
  changes.

### Plans, memberships, and payments

- Public catalog of active plans and administrator tools to create, update, and
  deactivate plans.
- Free plans can be activated without a paid checkout.
- Paid checkouts use Razorpay. The backend creates orders using the selected
  plan's server-side price and verifies the payment signature before activating
  or scheduling a membership.
- A new membership is scheduled after an existing active or scheduled
  membership. Users can retrieve their membership history.
- A background expiration job marks elapsed subscriptions as expired.
  Subscription status and premium access are reflected in the user profile and
  administrator dashboard.

### Administration and dashboards

- Role-protected administrator dashboard with totals for users, plans, active
  subscriptions, and expired subscriptions.
- Dashboard charts summarize user registrations and subscriptions over the last
  12 months. Additional panels show recent users, plan details, upcoming
  expirations, and recent expirations.
- Paginated user listing with search by name, email, phone, or ID; independent
  role and account-status filters; and total-count and pagination metadata.
- Administrator pages for dashboard reporting, user listing, plan management,
  and gallery management.

## Deployment and configuration

The backend requires a configured MySQL database. Optional integrations require
their own credentials and settings:

- Google and Facebook OAuth credentials and callback URLs.
- SMTP settings or a deployed Google Apps Script URL and shared secret.
- Razorpay server credentials and a separately configured frontend checkout
  key.
- Storj S3-compatible endpoint, bucket, and access credentials.

For production, configure a cryptographically random `JWT_SECRET_KEY`, exact
frontend origins in `CORS_ALLOWED_ORIGINS`, HTTPS cookie settings, and service
URLs through deployment environment variables. Never expose backend secrets in
the frontend or commit them to the repository. See the [README](../README.md)
for local setup, deployment, and integration configuration.

