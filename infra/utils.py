import os

Config = {
  "Production": os.getenv("ENV") == "production",
  "Account": os.getenv("AWS_ACCOUNT_ID"),
  "Region": os.getenv("AWS_REGION")
}
