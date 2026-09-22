# Oauth

# Flow

sequenceDiagram
  participant Client
  participant Provider as OAuth Provider
  participant Backend
  participant Database

  Client->>Backend: Request : for CLIENT_ID + REDIRECT_URL + Scopes
  Backend->>Client: Response : with CLIENT_ID + REDIRECT_URL
  Client->>Provider: Request : with CLIENT_ID + REDIRECT_URL + Scopes
  Note over Provider: Consent Screen
  Provider->>Client: Response : with ACCESS_TOKEN or REFRESH_TOKEN
  Client->>Backend: Request : with Provider's ACCESS_TOKEN or REFRESH_TOKEN
  Backend->>Provider: Request : with user's ACESS_TOKEN, for User's Info
  Provider->>Backend: Response : with User's Info
  Backend->>Database: Store : user's ACCESS_TOKEN + User's Info
  Backend->>Client: Response : with Backend's ACCESS_TOKEN


# What is Registration in Oauth ?

- No seperate registration route support.
- Only single `Continue with google` button 