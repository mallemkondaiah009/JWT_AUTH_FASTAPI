"""add role column to users

Revision ID: 427d2f3e0602
Revises: 
Create Date: 2026-02-13 10:44:48.259380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '427d2f3e0602'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_roles_enum = sa.Enum('user', 'admin', name='user_roles')

def upgrade() -> None:
    """Upgrade schema."""
    user_roles_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'users',
        sa.Column(
            'role',
            user_roles_enum,
            server_default='user',
            nullable=False
        )
    )


def downgrade():
    op.drop_column('users', 'role')
    user_roles_enum.drop(op.get_bind(), checkfirst=True)