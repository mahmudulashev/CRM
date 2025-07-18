"""init

Revision ID: d39f956bf8fc
Revises: 7b36627f7b04
Create Date: 2025-07-11 17:17:35.662785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd39f956bf8fc'
down_revision = '7b36627f7b04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('monthly_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('month', sa.String(length=7), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('attendance_percent', sa.Float(), nullable=True),
    sa.Column('avg_homework', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('group_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)

    with op.batch_alter_table('homework', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('group_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('homework', schema=None) as batch_op:
        batch_op.alter_column('group_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=True)

    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.alter_column('group_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=True)

    op.drop_table('monthly_report')
    # ### end Alembic commands ###
