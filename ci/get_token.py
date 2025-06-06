import os

os.environ["EBRAINS_AUTH_ENDPOINT"] = "https://iam-int.ebrains.eu/auth/realms/hbp"

from ebrains_iam.client_credential import ClientCredentialsSession

sess = ClientCredentialsSession(
    client_id=os.environ["EBRAINS_CLIENT_ID"], client_secret=os.environ["EBRAINS_CLIENT_SECRET"]
)
token = sess.get_token()

print(token)
