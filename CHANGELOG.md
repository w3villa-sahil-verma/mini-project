# Changelog

This changelog summarizes the project capabilities visible in the repository.
No release tags or prior versioned changelog entries were found, so this is a
baseline snapshot rather than a claim that every listed feature was added in a
single release.

## [Unreleased] — 2026-11-07 snapshot

### Added

- React, TypeScript, and Vite frontend with public gallery, home, login,
  registration, profile, pricing, and dashboard pages.
- FastAPI backend with SQLAlchemy and MySQL persistence.
- Email-and-password registration with an emailed registration link.
- Google and Facebook OAuth sign-in, provider identity persistence, and
  same-email account linking.
- HTTP-only access and refresh cookies, refresh-token rotation, logout, and
  password-reset links.
- Role-based admin pages and APIs for dashboard data, users, plans, and gallery
  management.
- Free and premium plan catalog, Razorpay checkout, server-side payment
  signature verification, subscription scheduling, and expiration processing.
- Profile and gallery image uploads through Storj-compatible pre-signed URLs,
  with backend verification of uploaded objects.
- Public paginated gallery browsing with bounded-size, watermarked WebP
  previews for premium images.
- Original-resolution downloads through a protected endpoint, available to
  Silver members for one hour and Gold members for three hours after
  subscription activation, bounded by subscription expiry.
- SMTP and Google Apps Script email provider configuration.
- Deployment configuration guidance for Vercel and Render.

### Changed

- Public visitors receive low-resolution previews instead of original
  gallery images.
- Premium image previews are watermarked, while original-resolution downloads
  require a current Silver or Gold entitlement.
- New subscriptions are scheduled after existing active or scheduled
  subscriptions.
- Authentication and API configuration are documented through environment
  variables, including CORS origins, OAuth callbacks, payment credentials, and
  object-storage settings.
- `/gallery` is the canonical gallery path; `/gallary` remains as a legacy
  alias.

### Validation

- Frontend production build completed in the reviewed environment.
- All 14 backend unit tests passed in the project virtual environment.
- The modified gallery page has one pre-existing hook lint error in its initial
  loading effect; the remaining page lint checks pass when that rule is
  excluded.

For detailed feature descriptions and setup instructions, see the
[release notes](./docs/RELEASE_NOTES.md) and [README](./README.md). For
repository-level risks and recommended follow-up, see the [project RCA](./docs/RCA.md).
