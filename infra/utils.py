import os

Config = {
  "Production": os.getenv("ENV") == "production"
}
