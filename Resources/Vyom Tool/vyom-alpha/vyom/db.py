import duckdb
import os
import json
import uuid
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

DB_PATH = os.path.expanduser("~/.vyom/vyom.duckdb")

def get_connection():
    """Establish connection to DuckDB and create schema if needed"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    
    # Create tables if they don't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id VARCHAR PRIMARY KEY,
            source_path VARCHAR,
            status VARCHAR,
            result JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_data (
            job_id VARCHAR PRIMARY KEY,
            data JSON,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversions (
            id VARCHAR PRIMARY KEY,
            job_id VARCHAR,
            format VARCHAR,
            output_path VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create saphire_comments table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saphire_comments (
            id VARCHAR PRIMARY KEY,
            job_id VARCHAR,
            element_path VARCHAR,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    return conn

def create_job(job_id, source_path):
    conn = get_connection()
    conn.execute("""
        INSERT INTO jobs (id, source_path, status, result)
        VALUES (?, ?, 'STARTED', '{}')
    """, (job_id, source_path))

def update_job_status(job_id, status, result=None):
    conn = get_connection()
    result_json = json.dumps(result or {})
    conn.execute("""
        UPDATE jobs
        SET status = ?, result = ?
        WHERE id = ?
    """, (status, result_json, job_id))

def get_job(job_id):
    conn = get_connection()
    result = conn.execute("""
        SELECT id, source_path, status, result
        FROM jobs
        WHERE id = ?
    """, (job_id,)).fetchone()
    
    if not result:
        return None
        
    return {
        'id': result[0],
        'source_path': result[1],
        'status': result[2],
        'result': json.loads(result[3])
    }

def get_job_status(job_id):
    """Get job status and merge with job data for the CLI status command.
    
    This function is specifically for the status command in the CLI,
    combining job metadata with any available job data.
    
    Args:
        job_id: Job ID to query
        
    Returns:
        dict: Job status information or None if not found
    """
    # Get basic job info
    job = get_job(job_id)
    if not job:
        return None
    
    # Merge with job data if available
    job_data = get_job_data(job_id)
    if job_data:
        # Add relevant data from job_data to the status
        if "metadata" in job_data:
            job["metadata"] = job_data["metadata"]
        if "saphire_data" in job_data:
            job["saphire_data"] = job_data["saphire_data"]
    
    return job

def save_job_data(job_id, data):
    conn = get_connection()
    data_json = json.dumps(data)
    
    # Check if record exists
    existing = conn.execute("""
        SELECT 1 FROM job_data WHERE job_id = ?
    """, (job_id,)).fetchone()
    
    if existing:
        conn.execute("""
            UPDATE job_data
            SET data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
        """, (data_json, job_id))
    else:
        conn.execute("""
            INSERT INTO job_data (job_id, data)
            VALUES (?, ?)
        """, (job_id, data_json))

def get_job_data(job_id):
    conn = get_connection()
    result = conn.execute("""
        SELECT data FROM job_data WHERE job_id = ?
    """, (job_id,)).fetchone()
    
    if not result:
        return None
        
    return json.loads(result[0])

def save_conversion(job_id, format, output_path):
    """Save information about a conversion"""
    conn = get_connection()
    conversion_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO conversions (id, job_id, format, output_path)
        VALUES (?, ?, ?, ?)
    """, (conversion_id, job_id, format, output_path))

def get_all_jobs():
    """Get all jobs from the database, sorted by creation time desc"""
    conn = get_connection()
    results = conn.execute("""
        SELECT id, source_path, status, result, created_at
        FROM jobs
        ORDER BY created_at DESC
    """).fetchall()
    
    if not results:
        return []
    
    jobs = []
    for row in results:
        jobs.append({
            'id': row[0],
            'source_path': row[1],
            'status': row[2],
            'result': json.loads(row[3]),
            'created_at': row[4]
        })
    
    return jobs

def save_comment(job_id, element_path, comment):
    """
    Save a comment to the DuckDB database.
    
    Args:
        job_id: Job ID the comment belongs to
        element_path: Path to the element being commented on
        comment: Comment text
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        
        # Check if a comment for this path already exists
        existing = conn.execute("""
            SELECT id FROM saphire_comments
            WHERE job_id = ? AND element_path = ?
        """, (job_id, element_path)).fetchone()
        
        if existing:
            # Update existing comment
            conn.execute("""
                UPDATE saphire_comments
                SET comment = ?, created_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (comment, existing[0]))
        else:
            # Insert new comment
            comment_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO saphire_comments (id, job_id, element_path, comment)
                VALUES (?, ?, ?, ?)
            """, (comment_id, job_id, element_path, comment))
        
        return True
    except Exception as e:
        logger.error(f"Error saving comment to database: {e}")
        return False

def get_comments_for_job(job_id):
    """
    Get all comments for a specific job.
    
    Args:
        job_id: Job ID to get comments for
        
    Returns:
        dict: Dictionary of element_path -> comment
    """
    try:
        conn = get_connection()
        
        # Fetch comments
        results = conn.execute("""
            SELECT element_path, comment
            FROM saphire_comments
            WHERE job_id = ?
        """, (job_id,)).fetchall()
        
        # Create a dictionary of comments
        comments = {}
        for row in results:
            comments[row[0]] = row[1]
            
        return comments
    except Exception as e:
        logger.error(f"Error getting comments from database: {e}")
        return {}
