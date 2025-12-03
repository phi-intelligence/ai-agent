"""Add local_agents table

Revision ID: 005_local_agents
Revises: 004_tasks
Create Date: 2024-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_local_agents'
down_revision = '004_tasks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create local_agents table
    op.create_table(
        'local_agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='ENROLLED'),
        sa.Column('last_heartbeat_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('local_agents')


