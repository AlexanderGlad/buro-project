"""Add secret table

Revision ID: c01c7b314ead
Revises: 
Create Date: 2023-12-06 02:50:44.862294

"""
import sqlalchemy as sa
import sqlmodel  # NEW
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c01c7b314ead'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('secret',
    sa.Column('secret', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('secret_phrase', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('secret_key', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secret_secret_key'), 'secret', ['secret_key'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_secret_secret_key'), table_name='secret')
    op.drop_table('secret')
    # ### end Alembic commands ###
