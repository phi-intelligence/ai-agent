"""Add task_metrics table

Revision ID: 006_task_metrics
Revises: 005_local_agents
Create Date: 2024-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_task_metrics'
down_revision = '005_local_agents'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create task_metrics table
    op.create_table(
        'task_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('llm_calls', sa.Integer(), server_default='0'),
        sa.Column('llm_tokens_used', sa.Integer(), server_default='0'),
        sa.Column('tool_calls', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('task_metrics')


