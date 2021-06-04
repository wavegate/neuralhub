"""migrate

Revision ID: 91778bec4909
Revises: 502c7db7aeb6
Create Date: 2021-06-03 23:37:34.290291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91778bec4909'
down_revision = '502c7db7aeb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mouse', schema=None) as batch_op:
        batch_op.alter_column('sex',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=500),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mouse', schema=None) as batch_op:
        batch_op.alter_column('sex',
               existing_type=sa.String(length=500),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
