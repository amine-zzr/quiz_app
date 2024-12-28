"""Add username field to User model

Revision ID: f68cb234b763
Revises: 8bb31f54f525
Create Date: 2024-12-28 19:51:03.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'f68cb234b763'
down_revision = '8bb31f54f525'
branch_labels = None
depends_on = None


def upgrade():
    # Create new table with username column
    op.execute('''
        CREATE TABLE user_new (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(128),
            created_at DATETIME,
            username VARCHAR(50) NOT NULL UNIQUE
        )
    ''')
    
    # Copy existing data and generate usernames
    connection = op.get_bind()
    users = connection.execute(text('SELECT id, email, password_hash, created_at FROM user')).fetchall()
    
    for user_id, email, password_hash, created_at in users:
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        # Check for username conflicts
        while connection.execute(
            text('SELECT id FROM user_new WHERE username = :username'),
            {'username': username}
        ).fetchone() is not None:
            username = f"{base_username}{counter}"
            counter += 1
        
        # Insert user with generated username
        connection.execute(
            text('''
                INSERT INTO user_new (id, email, password_hash, created_at, username)
                VALUES (:id, :email, :password_hash, :created_at, :username)
            '''),
            {
                'id': user_id,
                'email': email,
                'password_hash': password_hash,
                'created_at': created_at,
                'username': username
            }
        )
    
    # Drop old table and rename new one
    op.drop_table('user')
    op.execute('ALTER TABLE user_new RENAME TO user')


def downgrade():
    # Create table without username
    op.execute('''
        CREATE TABLE user_new (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(128),
            created_at DATETIME
        )
    ''')
    
    # Copy data without username
    op.execute('''
        INSERT INTO user_new (id, email, password_hash, created_at)
        SELECT id, email, password_hash, created_at FROM user
    ''')
    
    # Drop old table and rename new one
    op.drop_table('user')
    op.execute('ALTER TABLE user_new RENAME TO user')
