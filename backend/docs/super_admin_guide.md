# Super Admin Creation Guide

This guide explains how to create a super admin user for the Tweeza platform using the provided script.

## Prerequisites

- Python 3.8+ installed
- Access to the Tweeza backend code
- Database connection configured in environment variables

## Steps to Create a Super Admin

1. **Activate your virtual environment**

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

2. **Navigate to the backend directory**

```bash
cd path/to/Tweeza/backend
```

3. **Run the script with required parameters**

```bash
python scripts/create_super_admin.py \
    --email="admin@example.com" \
    --password="SecurePassword123!" \
    --name="Admin User" \
    --phone="+213555123456" \
    --location="Algiers, Algeria" \
    --latitude=36.7538 \
    --longitude=3.0588
```

Required parameters:

- `--email`: Admin's email address
- `--password`: Secure password for the admin account
- `--name`: Full name of the admin
- `--phone`: Phone number with country code

Optional parameters:

- `--location`: Description of the admin's location (default: "Default Location")
- `--latitude`: Geographic latitude (default: 0.0)
- `--longitude`: Geographic longitude (default: 0.0)

4. **Verify the admin was created**

You should see a confirmation message:

```
Super admin user admin@example.com created successfully.
```

Or if the user already exists:

```
Added super admin role to existing user admin@example.com.
```

## Security Best Practices

1. Use a strong password with mixed case, numbers, and special characters
2. Create super admin accounts only when necessary
3. Use a dedicated email address for the admin account
4. Change the default password immediately after first login
5. Only run this script in a secure environment

## Using the Super Admin Account

After creating the super admin account, you can log in to the web interface with the provided credentials. Super admins have the following privileges:

- Create, edit, or delete any organization
- Create, edit, or delete any user
- Manage roles and permissions for any user
- Access all platform features

## Troubleshooting

If you encounter an error like `Error creating super admin: ...`, check:

1. Database connection settings
2. That email and phone are not already registered
3. That the password meets security requirements
4. That you have the correct permissions to access the database
