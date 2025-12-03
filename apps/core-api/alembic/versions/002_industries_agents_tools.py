"""Add industries, role templates, tools, agents, agent_tools

Revision ID: 002_industries_agents_tools
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_industries_agents_tools'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create industries table
    op.create_table(
        'industries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
    )
    op.create_index(op.f('ix_industries_key'), 'industries', ['key'], unique=True)
    
    # Create role_templates table
    op.create_table(
        'role_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('industry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('default_capabilities', postgresql.JSONB(), nullable=True),
        sa.Column('default_tools', postgresql.JSONB(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['industry_id'], ['industries.id'], ),
    )
    
    # Create tools table
    op.create_table(
        'tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('config_schema', postgresql.JSONB(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
    )
    op.create_index(op.f('ix_tools_key'), 'tools', ['key'], unique=True)
    
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('industry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='ACTIVE'),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['industry_id'], ['industries.id'], ),
        sa.ForeignKeyConstraint(['role_template_id'], ['role_templates.id'], ),
    )
    
    # Create agent_tools table
    op.create_table(
        'agent_tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ),
    )


def downgrade() -> None:
    op.drop_table('agent_tools')
    op.drop_table('agents')
    op.drop_index(op.f('ix_tools_key'), table_name='tools')
    op.drop_table('tools')
    op.drop_table('role_templates')
    op.drop_index(op.f('ix_industries_key'), table_name='industries')
    op.drop_table('industries')


