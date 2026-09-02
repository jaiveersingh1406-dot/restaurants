from fastapi import HTTPException

from app.db.db import get_connection
from app.core.security import hash_password, verify_or_upgrade_password


def _public_user(row: dict, role: str) -> dict:
    return {
        "id": row["id"],
        "name": row.get("name") or row.get("username"),
        "email": row["email"],
        "phone": row.get("phone"),
        "role": role,
    }


def _upgrade_hash(table: str, column: str, user_id: int, new_hash: str):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"UPDATE {table} SET {column} = %s WHERE id = %s",
            (new_hash, user_id),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_signup(name: str, email: str, password: str):
    """Register a customer account"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s", (email,)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail="An account with this email already exists",
                )

            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (name, email, hash_password(password)),
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while signing up: {exc}",
        ) from exc


def check_email_exists(email: str) -> bool:
    """Check if an email exists in users or admin table"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return True
            cursor.execute("SELECT id FROM admin WHERE email = %s", (email,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while checking email: {exc}",
        ) from exc


def change_password(email: str, role: str, old_password: str, new_password: str):
    """Verify old password and update to a new hashed password"""
    table = "admin" if role == "admin" else "users"

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT * FROM {table} WHERE email = %s",
                (email,),
            )
            user_row = cursor.fetchone()

            if not user_row:
                raise HTTPException(status_code=404, detail="Account not found")

            is_valid = verify_or_upgrade_password(
                old_password,
                user_row["password"],
            )

            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail="Current password is incorrect",
                )

            cursor.close()

            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {table} SET password = %s WHERE id = %s",
                (hash_password(new_password), user_row["id"]),
            )
            connection.commit()

            return {"message": "Password updated successfully"}
        finally:
            cursor.close()
            connection.close()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while changing password: {exc}",
        ) from exc


def authenticate(email: str, password: str, role: str):
    """Authenticate against admin or users table; returns (user, token_payload_role)."""
    table = "admin" if role == "admin" else "users"

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT * FROM {table} WHERE email = %s",
                (email,),
            )
            user_row = cursor.fetchone()

            if not user_row:
                return None

            is_valid = verify_or_upgrade_password(
                password,
                user_row["password"],
                upgrade_callback=lambda new_hash: _upgrade_hash(
                    table, "password", user_row["id"], new_hash
                ),
            )

            if not is_valid:
                return None

            resolved_role = "admin" if table == "admin" else "user"
            return _public_user(user_row, resolved_role)
        finally:
            cursor.close()
            connection.close()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while logging in: {exc}",
        ) from exc


def update_user_profile(email: str, phone: str = None):
    """Update the phone number for a customer account."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()

        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute(
            "UPDATE users SET phone = %s WHERE id = %s",
            (phone, row["id"]),
        )
        connection.commit()

        cursor.close()
        connection.close()

        return _public_user({**row, "phone": phone}, "user")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while updating profile: {exc}",
        ) from exc


def get_profile(email: str, role: str):
    """Return the full public profile for a user or admin."""
    table = "admin" if role == "admin" else "users"

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
            row = cursor.fetchone()

            if not row:
                return None

            return _public_user(row, role)
        finally:
            cursor.close()
            connection.close()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error while loading profile: {exc}",
        ) from exc
