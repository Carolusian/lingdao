
DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "624b974c-8077-4b88-9a18-cc1273da702ba8eb47a0-2551-4043-9c4d-2b7c65d67439ace56b31-746d-4376-881f-c506c7ce9604"
NEVERCACHE_KEY = "e4ec8791-3fd7-4b86-9473-1995e019c13a3dcb691f-60db-4a3f-a657-6d470256f28be1c1ca84-beb1-4376-a492-312d74cc8562"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "dev.db",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}
