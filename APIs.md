
`POST : /api/v1/users`

query : 

    - type = social | standard
    - action = signup

body : 

    type = social
    code : String

    type = standard
    email : String
    password : String


description : 

    - handle both social and standard signup

---

`POST : /api/v1/users`

query :

    - type = social | standard
    - action = login

body : 

    type = social
    code : String

    type = standard
    email : String
    password : String

description :

    - handle both social and standard login

---

`GET : /api/v1/users`

query :

    - action = verification
    - code : String  // Verification code


description : 

    - handle email verification of Standard accounts.

--- 

`PATCH : /api/v1/users/{id}`

description : 

    - Update user details
    - According to role of User attributes will be update

---

`DELETE : /api/v1/users/{id}`

description : 

    - delete an user with ADMIN role