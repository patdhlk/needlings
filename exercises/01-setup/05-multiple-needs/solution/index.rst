==================
End of chapter 1!
==================

.. req:: User can log in
   :id: REQ_LOGIN

   A registered user authenticates with email and password.

.. req:: User can log out
   :id: REQ_LOGOUT

   A logged-in user can end their session from any page.

.. spec:: Session cookie spec
   :id: SPEC_SESSION

   Session cookie is HttpOnly, Secure, SameSite=Lax, 24h TTL.
