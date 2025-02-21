"""Create dataset model

Revision ID: 849f3b72f89f
Revises: 8ea7a1a1a2a4
Create Date: 2021-01-27 14:54:41.422673

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '849f3b72f89f'
down_revision = '8ea7a1a1a2a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dataset',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('spreadsheet_id', sa.String(), nullable=False),
    sa.Column('spreadsheet_range', sa.String(), nullable=False),
    sa.Column('spreadsheet_hash', sa.String(length=64), nullable=False),
    sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dataset_spreadsheet_hash'), 'dataset', ['spreadsheet_hash'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_dataset_spreadsheet_hash'), table_name='dataset')
    op.drop_table('dataset')
    # ### end Alembic commands ###
