"""initial schema: users, rooms, room_members, chat_messages

Revision ID: 0001
Revises:
Create Date: 2026-06-17

"""

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        CREATE TABLE users (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          google_sub TEXT UNIQUE NOT NULL,
          email TEXT UNIQUE NOT NULL,
          name TEXT NOT NULL,
          avatar_url TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE TABLE rooms (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          host_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          name TEXT NOT NULL,
          current_video_id TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_rooms_host ON rooms(host_id);

        CREATE TABLE room_members (
          room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          PRIMARY KEY (room_id, user_id)
        );
        CREATE INDEX idx_room_members_user ON room_members(user_id);

        CREATE TABLE chat_messages (
          id BIGSERIAL PRIMARY KEY,
          room_id UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          body TEXT NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_chat_messages_room_created ON chat_messages(room_id, created_at);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS chat_messages;
        DROP TABLE IF EXISTS room_members;
        DROP TABLE IF EXISTS rooms;
        DROP TABLE IF EXISTS users;
        """
    )
