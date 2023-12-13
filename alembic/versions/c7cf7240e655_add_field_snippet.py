"""add field snippet

Revision ID: c7cf7240e655
Revises: 
Create Date: 2023-12-13 14:48:34.996085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Text


# revision identifiers, used by Alembic.
revision: str = 'c7cf7240e655'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("questions", Column("snippet", Text()))


def downgrade() -> None:
    pass
