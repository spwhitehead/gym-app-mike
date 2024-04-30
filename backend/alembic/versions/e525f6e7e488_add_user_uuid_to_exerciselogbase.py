"""add user_uuid to ExerciseLogBase

Revision ID: e525f6e7e488
Revises: 
Create Date: 2024-04-30 14:06:11.297916

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa
import models


# revision identifiers, used by Alembic.
revision: str = 'e525f6e7e488'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Enable batch mode for operations not supported by SQLite
    with op.batch_alter_table("exerciselog", schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_uuid', models.utility.GUID(), nullable=True))
        # Providing a name for the foreign key constraint
        batch_op.create_foreign_key(
            'fk_user_uuid', 'user', ['user_uuid'], ['uuid'], ondelete='CASCADE'
        )

def downgrade():
    with op.batch_alter_table("exerciselog", schema=None) as batch_op:
        # Refer to the foreign key constraint by the name provided during the upgrade
        batch_op.drop_constraint('fk_user_uuid', type_='foreign_key')
        batch_op.drop_column('user_uuid')