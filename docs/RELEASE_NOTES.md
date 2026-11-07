# Project Release Notes

**Release:** Current repository snapshot (no version or release tag specified)  
**Date:** 2026-11-07

## Overview

This project provides a photography gallery and membership-management
application. Visitors can browse free images, members can access premium
collections while their subscription is active, and administrators can manage
gallery content, users, plans, and dashboard data.

The application consists of a React, TypeScript, and Vite frontend and a
FastAPI backend using SQLAlchemy and MySQL. Image files are stored using a
Storj-compatible S3 API.

## Features

### Accounts and authentication

- Email-and-password registration with an emailed registration link.
- Google and Facebook OAuth sign-in, including linking provider identities to
  an existing account with the same email.
- HTTP-only access and refresh cookies, single-use refresh-token rotation,
  logout, and frontend retry after an expired access token.
- Password reset links that expire after 30 minutes and are consumed once;
  password changes invalidate outstanding refresh tokens.

### Memberships and payments

- Public plan catalog and authenticated checkout using Razorpay.
- Free plans can be activated without a paid checkout.
- Backend-side payment signature verification before paid membership activation.
- Membership scheduling after existing active or scheduled subscriptions, with
  expiration processing and subscription history.

### Profiles and image storage

- User profile management and profile-image upload using short-lived Storj
  pre-signed URLs.
- Server-side checks of uploaded image type and size before an image is marked
  ready.
- JPEG, PNG, and WebP uploads up to 5 MB; profile images can use configured
  public delivery or signed URLs.

### Gallery

- Public, paginated gallery browsing with an infinite-scroll experience.
- All visitors receive low-resolution WebP previews, with watermarks on
  premium images.
- Silver members can download original-resolution images for one hour and Gold
  members for three hours after membership activation, bounded by subscription
  expiry.
- Admin gallery tools for bulk upload, pagination, premium/free classification,
  and individual or bulk deletion.
- `/gallery` is the current route; `/gallary` remains as a legacy alias.

### Administration

- Role-protected admin dashboard with user, plan, and subscription summaries,
  recent activity, and upcoming expirations.
- Paginated user listing with search, role, and account-status filters.
- Plan management and subscription-expiry visibility.

## Deployment and configuration

The backend requires a configured MySQL database. Optional integrations require
their own credentials and settings:

- Google/Facebook OAuth application credentials and callback URLs.
- SMTP or Google Apps Script email delivery.
- Razorpay server credentials and a separately configured frontend checkout
  key.
- Storj S3-compatible endpoint, bucket, and access credentials.

For production, configure a cryptographically random `JWT_SECRET_KEY`, exact
frontend origins in `CORS_ALLOWED_ORIGINS`, HTTPS cookie settings, and service
URLs through deployment environment variables. Never expose backend secrets in
the frontend or commit them to the repository. See the [README](../README.md)
for local setup and integration configuration.

## Validation status

This note describes capabilities present in the repository; it does not certify
a production deployment. The frontend production build completed and all 14
backend unit tests passed in the project virtual environment. The modified
gallery page still reports a pre-existing hook lint error in its initial-load
effect; its other lint checks pass when that rule is excluded. See the
[project RCA](./RCA.md) for the assessment scope and recommended follow-up
actions.
