# Send Registration Link — Edge Cases

## CASE 1: Registration Link Has Never Been Sent

* Send a registration link to the user.
* Set `Account.email_verification_status = PENDING` when the account is created.

## CASE 2: Registration Link Was Sent, but the User Did Not Receive It

* Allow the user to resend the registration link after a few seconds.

## CASE 3: Registration Link Was Sent and Received, but the User Clicks "Send Registration Link" Again

* Increase the waiting period before allowing the user to resend the registration link.

## CASE 4: User Is Already Registered and Tries to Send a Registration Link

* Do not send a registration link.
* Display a warning: **"User is already registered."**
* Set `Account.email_verification_status = SUCCESS`.

## CASE 5: Registration Link Has Expired

* Display the **"Resend Registration Link"** option.
* Delete the user record where `Account.email_verification_status = PENDING` after the registration link expires.

## CASE 6: User Provides an Invalid Email Address

* Create a user record with only the email address and send the registration email.
* If the email is not verified within 1 hour, permanently delete the user.
* Delete the user record where `Account.email_verification_status = PENDING` after the link expires.
