"""
Tests for database functionality
"""
import os
import json
import uuid
import tempfile
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom import db

# Override the DB_PATH for testing
db.DB_PATH = os.path.join(tempfile.gettempdir(), f"vyom_test_{uuid.uuid4()}.duckdb")

def test_db_connection():
    """Test database connection and schema creation"""
    conn = db.get_connection()
    assert conn is not None, "Connection should not be None"
    
    # Check if tables were created
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    assert "jobs" in table_names, "jobs table should exist"
    assert "job_data" in table_names, "job_data table should exist"
    assert "conversions" in table_names, "conversions table should exist"

def test_job_creation_and_retrieval():
    """Test creating and retrieving a job"""
    job_id = f"test_{uuid.uuid4()}"
    source_path = "/path/to/test.zip"
    
    # Create a job
    db.create_job(job_id, source_path)
    
    # Retrieve the job
    job = db.get_job(job_id)
    assert job is not None, "Job should not be None"
    assert job["id"] == job_id, "Job ID should match"
    assert job["source_path"] == source_path, "Source path should match"
    assert job["status"] == "STARTED", "Initial status should be STARTED"

def test_job_status_update():
    """Test updating job status"""
    job_id = f"test_{uuid.uuid4()}"
    source_path = "/path/to/test.zip"
    
    # Create a job
    db.create_job(job_id, source_path)
    
    # Update job status
    result = {"processed": 42}
    db.update_job_status(job_id, "PROCESSING", result)
    
    # Retrieve the job
    job = db.get_job(job_id)
    assert job["status"] == "PROCESSING", "Status should be updated"
    assert job["result"]["processed"] == 42, "Result should be updated"

def test_job_data_storage_and_retrieval():
    """Test storing and retrieving job data"""
    job_id = f"test_{uuid.uuid4()}"
    source_path = "/path/to/test.zip"
    
    # Create a job
    db.create_job(job_id, source_path)
    
    # Save job data
    test_data = {
        "files": {
            "test.json": {
                "type": "json",
                "size": 100
            }
        },
        "metadata": {
            "total_files": 1
        }
    }
    db.save_job_data(job_id, test_data)
    
    # Retrieve job data
    retrieved_data = db.get_job_data(job_id)
    assert retrieved_data is not None, "Job data should not be None"
    assert retrieved_data["files"]["test.json"]["type"] == "json", "File type should match"
    assert retrieved_data["metadata"]["total_files"] == 1, "Metadata should match"
    
    # Update job data
    test_data["files"]["another.json"] = {"type": "json", "size": 200}
    test_data["metadata"]["total_files"] = 2
    db.save_job_data(job_id, test_data)
    
    # Retrieve updated job data
    retrieved_data = db.get_job_data(job_id)
    assert len(retrieved_data["files"]) == 2, "Updated files count should match"
    assert retrieved_data["metadata"]["total_files"] == 2, "Updated metadata should match"

def test_conversion_storage():
    """Test storing conversion data"""
    job_id = f"test_{uuid.uuid4()}"
    source_path = "/path/to/test.zip"
    format_type = "openpra"
    output_path = "/path/to/output.json"
    
    # Create a job
    db.create_job(job_id, source_path)
    
    # Save conversion
    conversion_id = db.save_conversion(job_id, format_type, output_path)
    assert conversion_id is not None, "Conversion ID should not be None"
    
    # Query the database directly to verify
    conn = db.get_connection()
    result = conn.execute("""
        SELECT job_id, format, output_path
        FROM conversions
        WHERE id = ?
    """, (conversion_id,)).fetchone()
    
    assert result is not None, "Conversion record should exist"
    assert result[0] == job_id, "Job ID should match"
    assert result[1] == format_type, "Format should match"
    assert result[2] == output_path, "Output path should match"

def cleanup():
    """Clean up test database"""
    try:
        os.unlink(db.DB_PATH)
    except:
        pass

if __name__ == "__main__":
    try:
        test_db_connection()
        test_job_creation_and_retrieval()
        test_job_status_update()
        test_job_data_storage_and_retrieval()
        test_conversion_storage()
        print("All database tests passed!")
    finally:
        cleanup() 