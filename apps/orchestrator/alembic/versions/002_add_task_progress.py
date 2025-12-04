"""Add progress tracking to tasks

Revision ID: 002_add_task_progress
Revises: 001_tool_tasks
Create Date: 2024-12-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_task_progress'
down_revision = '002_task_metrics'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add progress tracking columns to tasks table
    op.add_column('tasks', sa.Column('progress', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('tasks', sa.Column('eta_seconds', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('current_step', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'current_step')
    op.drop_column('tasks', 'eta_seconds')
    op.drop_column('tasks', 'progress')

