"""
Seed script for initial data: industries, role templates, and tools
Run this after migrations: python scripts/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Industry, RoleTemplate, Tool


def seed_data():
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        existing_industry = db.query(Industry).filter(Industry.key == "logistics").first()
        if existing_industry:
            print("Data already seeded. Skipping...")
            return
        
        # Create Logistics industry
        logistics_industry = Industry(
            key="logistics",
            name="Logistics & Warehousing",
            description="Supply chain, warehouse operations, and logistics management"
        )
        db.add(logistics_industry)
        db.flush()
        
        # Create role templates for logistics
        warehouse_analyst = RoleTemplate(
            industry_id=logistics_industry.id,
            key="warehouse_analyst",
            name="Warehouse Analyst",
            default_capabilities={
                "data_analysis": True,
                "reporting": True,
                "inventory_tracking": True
            },
            default_tools={
                "required": ["db", "file"],
                "optional": ["cctv"]
            },
            description="Analyzes warehouse operations, inventory, and performance metrics"
        )
        db.add(warehouse_analyst)
        
        ops_manager = RoleTemplate(
            industry_id=logistics_industry.id,
            key="ops_manager",
            name="Operations Manager",
            default_capabilities={
                "workflow_management": True,
                "team_coordination": True,
                "performance_monitoring": True
            },
            default_tools={
                "required": ["db", "email"],
                "optional": ["file"]
            },
            description="Manages daily operations, coordinates teams, and monitors performance"
        )
        db.add(ops_manager)
        
        safety_officer = RoleTemplate(
            industry_id=logistics_industry.id,
            key="safety_officer",
            name="Safety Officer",
            default_capabilities={
                "safety_monitoring": True,
                "incident_tracking": True,
                "compliance_reporting": True
            },
            default_tools={
                "required": ["db", "file"],
                "optional": ["cctv", "email"]
            },
            description="Monitors safety compliance, tracks incidents, and ensures regulatory adherence"
        )
        db.add(safety_officer)
        
        # Create tools
        db_tool = Tool(
            key="db",
            name="Database",
            config_schema={
                "type": "object",
                "properties": {
                    "dsn": {"type": "string", "description": "Database connection string"},
                    "host": {"type": "string"},
                    "port": {"type": "integer"},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string", "format": "password"}
                },
                "required": ["dsn"]
            },
            description="Access to database for querying and data retrieval"
        )
        db.add(db_tool)
        
        file_tool = Tool(
            key="file",
            name="File System",
            config_schema={
                "type": "object",
                "properties": {
                    "base_path": {"type": "string", "description": "Base directory path"},
                    "allowed_extensions": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["base_path"]
            },
            description="Read and write files from local file system"
        )
        db.add(file_tool)
        
        cctv_tool = Tool(
            key="cctv",
            name="CCTV",
            config_schema={
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "CCTV system API endpoint"},
                    "api_key": {"type": "string", "format": "password"}
                },
                "required": ["endpoint"]
            },
            description="Access to CCTV camera feeds and recordings (stub for now)"
        )
        db.add(cctv_tool)
        
        email_tool = Tool(
            key="email",
            name="Email",
            config_schema={
                "type": "object",
                "properties": {
                    "smtp_server": {"type": "string"},
                    "smtp_port": {"type": "integer"},
                    "username": {"type": "string"},
                    "password": {"type": "string", "format": "password"}
                },
                "required": ["smtp_server", "smtp_port", "username", "password"]
            },
            description="Send and receive emails"
        )
        db.add(email_tool)
        
        db.commit()
        print("✅ Successfully seeded industries, role templates, and tools!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()


