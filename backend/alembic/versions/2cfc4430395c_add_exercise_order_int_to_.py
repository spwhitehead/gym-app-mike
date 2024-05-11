"""add exercise_order int to workoutexercise table

Revision ID: 2cfc4430395c
Revises: 90766b4a23b4
Create Date: 2024-05-10 15:12:24.997095

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cfc4430395c'
down_revision: Union[str, None] = '90766b4a23b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workoutexercise', sa.Column('exercise_order', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_workoutexercise_exercise_order'), 'workoutexercise', ['exercise_order'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_workoutexercise_exercise_order'), table_name='workoutexercise')
    op.drop_column('workoutexercise', 'exercise_order')
    # ### end Alembic commands ###