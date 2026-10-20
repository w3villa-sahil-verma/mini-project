# Mini Project - Feature Requirement Document

## Overview
This document outlines the detailed requirements for developing the user signup, login,
profile management, pricing plan management, and admin panel processes for a web
application. The backend should store data securely and manage user sessions, profile
data, payments, and access control. It also includes a cron job for plan expiration. Each
feature is described in terms of its functionality, expected behavior, acceptance criteria,
and how it integrates with other features.

## 1. Signup Process
### 1.1 Social Signup (Account Merge)

Requirement: Implement the ability for users to sign up using their social media
accounts (e.g., Facebook, Google).
●​ Functionality: If an account with the same email already exists, the system should
merge the social media account with the existing account.
●​ Expected Behavior: Users should be able to seamlessly create an account or merge
with an existing one using their social media credentials.
●​ Acceptance Criteria:
○​ Users can sign up using at least two social media platforms.
○​ If an email already exists, the accounts are merged without data loss.
○​ Users are redirected to the dashboard after successful signup.

### 1.2 Standard Signup 
●​ Requirement: Allow users to sign up by providing their email address and creating a
password.
●​ Functionality: Upon successful signup, the system should send a confirmation email to
the user.
●​ Expected Behavior: Users receive a confirmation email and must confirm their email
address to activate their account.
●​ Acceptance Criteria:
○​ Users can sign up with an email and password.
○​ Confirmation email is sent to the registered email address.
○​ Users can confirm their email and activate their account by clicking the link in the
email.

## 2. Account Verification2.1 Email Verification through Link
●​ Requirement: Implement email verification through a verification link.
●​ Functionality: After signup, send a verification link to the user’s registered email
address. The user must click this link to verify their email.
●​ Expected Behavior: The system validates the link and marks the email as verified.
●​ Acceptance Criteria:
○​ A verification link is sent to the registered email after signup.
○​ Users can click the verification link to verify their email address.
○​ The system confirms the email verification upon clicking the link.

## 3. Login
### 3.1 Login
●​ Requirement: Allow verified users to log in using their email and password or through
social media accounts.
●​ Functionality: Implement authentication mechanisms for standard and social media
logins.
●​ Expected Behavior: Users can log in successfully if their credentials are correct and
their account is verified.
●​ Acceptance Criteria:
○​ Users can log in using email and password.
○​ Users can log in using social media accounts.
○​ Only verified accounts can access the dashboard after login.

## 4. Profile Management
### 4.1 Profile Picture Upload (Storj Integration)
●​ Requirement: Provide users with the ability to upload a profile picture, which is stored
on Storj.
●​ Functionality: Store the uploaded profile picture on Storj and display it as a thumbnail in
the user’s profile.
●​ Expected Behavior: Users can see their uploaded profile picture in their profile and on
the user listing page.
●​ Acceptance Criteria:
○​ Users can upload a profile picture.
○​ The profile picture is stored on Storj and displayed as a thumbnail in the user’s
profile.
○​ The profile picture is visible on the user listing page.

### 4.2 Profile Management (Address, Auto Suggestion, Display in Map)
●​ Requirement: Allow users to manage their profile details, including address information.
●​ Functionality: Implement auto-suggestions for the address field and display the location
on a map using Google Maps API.
●​ Expected Behavior: Users can update their address details, receive auto-suggestions,
and see their location on a map.
●​ Acceptance Criteria:
○​ Users can update their address details.
○​ Address field provides auto-suggestions as the user types.
○​ The address is displayed on a map within the profile.

### 4.3 Profile Download
●​ Requirement: Enable users to download their profile information in a specified format.
●​ Functionality: Provide an option for users to export their profile data.
●​ Expected Behavior: Users can download their profile information in a well-formatted
document.
●​ Acceptance Criteria:
○​ Users can request to download their profile information.
○​ Profile data is exported in a user-friendly format.
○​ Downloaded profile includes all relevant user details.

## 5. Payment Processing and Pricing Plans
### 5.1 Payment Gateway Integration
●​ Requirement: Integrate a payment gateway, such as Stripe, to process payments for
pricing plans.
●​ Functionality: Handle transactions securely and update the user's access level based
on the payment made.
●​ Expected Behavior: Users can make payments, and their account is upgraded to the
appropriate access level upon successful payment.
●​ Acceptance Criteria:
○​ Users can initiate payments through the payment gateway.
○​ Payment transactions are secure and processed correctly.
○​ User access level is upgraded immediately upon successful payment.

### 5.2 Pricing Plans with Time-Limited Access
●​ Requirement: Provide time-limited pricing plans with varying benefits. Plans should
expire after a set duration (1 hour, 6 hours, or 12 hours).
●​ Functionality: Upon payment, the selected plan (Free, Silver, Gold) is activated and
expires automatically based on its duration.●​ Expected Behavior: Users can select a pricing plan, and the system automatically
disables access when the plan’s time expires.
●​ Acceptance Criteria:
○​ Users can select and pay for a plan (Free, Silver, Gold).
○​ Plans activate immediately upon payment and are stored in the user profile.
○​ The system runs a cron job to check plan durations and automatically expire
plans after 1 hour, 6 hours, or 12 hours.
○​ The plan status is stored in the user’s profile and displayed in the admin panel.

## 6. Admin Panel
### 6.1 Admin Role
●​ Requirement: Implement an admin role with special privileges to manage the
application.
●​ Functionality: Admins can log in with their credentials to access the admin panel.
●​ Expected Behavior: Admins have access to advanced management features within the
application.
●​ Acceptance Criteria:
○​ Admins can log in with special credentials.
○​ Admin panel is accessible only to admin users.
○​ Admins have access to user management and other administrative features.

### 6.2 User Listing with Search, Filter, and Pagination
●​ Requirement: Provide an interface for admins to view a list of all users.
●​ Functionality: Implement search, filter, and pagination functionalities to help admins
manage users effectively.
●​ Expected Behavior: Admins can search for users, apply filters, and navigate through
pages of user listings.
●​ Acceptance Criteria:
○​ Admins can view all users in a list.
○​ Admins can search and filter users based on various criteria.
○​ User list is paginated for easy navigation.

### 6.3 User Listing
●​
●​
●​
●​
Requirement: Display all users in a list format.
Functionality: Show basic information of each user in the list.
Expected Behavior: Admins can see a comprehensive list of users with basic details.
Acceptance Criteria:
○​ All users are displayed in a list.
○​ Basic information such as name, email, and status is shown for each user.6.4 User Listing Search
●​ Requirement: Enable admins to search for specific users using various criteria.
●​ Functionality: Implement search functionality based on name, email, or other relevant
fields.
●​ Expected Behavior: Admins can quickly find specific users using the search feature.
●​ Acceptance Criteria:
○​ Admins can search users by name, email, or other criteria.
○​ Search results are accurate and displayed quickly.


### 6.5 User Listing with Pagination
●​ Requirement: Implement pagination for the user listing to manage large numbers of
users efficiently.
●​ Functionality: Allow admins to navigate through different pages of the user list.
●​ Expected Behavior: Admins can easily browse through user information in a paginated
format.
●​ Acceptance Criteria:
○​ User list is divided into pages.
○​ Admins can navigate between pages to view more users.
○​ Pagination controls are user-friendly and responsive.

## 7. Cron Job for Plan Expiration
### 7.1 Plan Expiration Cron Job
●​ Requirement: Implement a cron job to check for expired plans based on their duration
(1 hour, 6 hours, 12 hours) and deactivate them accordingly.
●​ Functionality: The cron job should run periodically to validate plan expiration times and
revoke access to expired plans.
●​ Expected Behavior: Plans expire at the end of their duration, and users lose access to
premium features if the plan expires.
●​ Acceptance Criteria:
○​ The cron job runs at regular intervals to check for plan expirations.
○​ Plans are deactivated automatically once their duration (1 hour, 6 hours, or 12
hours) ends.
○​ Expired plans update the user’s profile and reflect in the admin panel.

# FAQQ: Which social login options should we implement? ​
A: You can choose your own social login options, but Facebook and Google are recommended
as they are easier to implement than others.
Q: Which payment gateway should we use? ​
A: Stripe's free/sandbox version is recommended for handling payments.
Q: Which service should be used for address updates and suggestions? ​
A: Google Maps API should be used for auto-suggestions and map pin display for address
updates.
Q: Where should user files, like profile pictures, be stored? ​
A: Storj is recommended for storing user files securely.
Q: Are there any special offerings on the pricing plans? ​
A: There are no special offerings. Users can pay for the plan of their choice, and plan details
must be stored and linked with the user.
Q: How should user search functionality be handled in the admin panel? ​
A: User search by name should be managed with filters and pagination. Refreshing the page
should not reset search criteria or pagination.
Q: How long do the pricing plans last, and how is this managed? ​
A: Pricing plans have time limits of 1 hour, 6 hours, or 12 hours. A cron job will manage plan
expiration and automatically revoke access when a plan's duration ends.