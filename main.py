import argparse
import os
import subprocess
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Launch Django with custom environment variables."
    )

    # Add optional arguments with defaults
    parser.add_argument(
        "--secret-key",
        type=str,
        default="default-dev-secret-key-123",
        help="Custom Django SECRET_KEY environment variable",
    )
    parser.add_argument(
        "--port",
        type=str,
        default="8000",
        help="Port for the Django server (default: 8000)",
    )

    return parser.parse_args()


def start_django_server():
    args = parse_arguments()

    # 1. Define your custom environment variables
    custom_env = os.environ.copy()  # Copy the current system environment
    custom_env["DEBUG"] = 'false'
    custom_env["SECRET_KEY"] = args.secret_key
    custom_env["DJANGO_SETTINGS_MODULE"] = "ppm_app.settings.cli"
    custom_env["PYTHONWARNINGS"] = "ignore"
    # These exact variables are read by Django's `createsuperuser --noinput` command
    custom_env["DJANGO_SUPERUSER_USERNAME"] = "admin"
    custom_env["DJANGO_SUPERUSER_PASSWORD"] = "12345"
    custom_env["DJANGO_SUPERUSER_EMAIL"] = "admin@example.com"

    print("🌙 Starting Dreamy CLI version...")
    print("💿 A SQLite database will keep your data locally as 'cli.sqlite3'")
    print("Collecting static files...")

    try:
        cmd_static = [sys.executable, "src/manage.py", "collectstatic", "--noinput", "--clear"]
        subprocess.run(cmd_static, env=custom_env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during static files collection: {e}")
        return

    try:
        # Step A: Run migrations (can't make a user without a user table!)
        print("🔄 Running database migrations...")
        subprocess.run(
            [sys.executable, "src/manage.py", "migrate"],
            env=custom_env,
            check=True,
        )

        # Step B: Attempt to create the superuser non-interactively
        print("👤 Checking/Creating superuser...")
        subprocess.run(
            [sys.executable, "src/manage.py", "createsuperuser", "--noinput"],
            env=custom_env,
            # We don't use check=True here because if the admin already exists,
            # Django exits with a failure code. We want to skip that and keep going.
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("✓ Superuser setup complete (or already exists).")
    except Exception as e:
        print(e)

    print(f"🚀 Starting Django server on port {args.port}...")
    print(f"🔑 Using SECRET_KEY: {args.secret_key[:10]}...")
    print(f"🪲 Using DEBUG: {args.debug}")

    try:
        # env=custom_env injects your variables into the command's context
        subprocess.run([sys.executable, "src/manage.py", "runserver",
                        args.port], env=custom_env, check=True)
    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C without printing a massive Python stack trace
        print("\n🛑 Server stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server exited with an error: {e}")


if __name__ == "__main__":
    start_django_server()
