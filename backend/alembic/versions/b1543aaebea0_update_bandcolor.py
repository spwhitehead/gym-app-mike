"""update bandcolor

Revision ID: b1543aaebea0
Revises: 
Create Date: 2024-05-08 11:06:21.863751

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1543aaebea0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('equipment', sa.Column('band_color_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_equipment_band_color_id'), 'equipment', ['band_color_id'], unique=False)
    op.create_foreign_key(None, 'equipment', 'bandcolor', ['band_color_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'equipment', type_='foreignkey')
    op.drop_index(op.f('ix_equipment_band_color_id'), table_name='equipment')
    op.drop_column('equipment', 'band_color_id')
    # ### end Alembic commands ###
