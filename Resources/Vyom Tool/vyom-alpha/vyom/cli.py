import click
import os
import time
import json
import logging
import datetime
import pkg_resources
from pathlib import Path
from . import db
from . import extractor
from . import converter
from . import viewer
from . import session
from .schema import openpra
from typing import Optional

VERSION = pkg_resources.get_distribution("vyom").version

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Exports directory - this should be created if it doesn't exist
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'exports')

def get_timestamped_filename(base_name, file_type, extension="json"):
    """
    Generate a timestamped filename for exports.
    
    Args:
        base_name: Base name for the file (usually project or job ID)
        file_type: Type of export (e.g., openpra, saphire)
        extension: File extension (default: json)
        
    Returns:
        str: Timestamped filename
    """
    # Create exports directory if it doesn't exist
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # Generate timestamp in format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create filename
    filename = f"{base_name}_{file_type}_{timestamp}.{extension}"
    
    # Return full path
    return os.path.join(EXPORTS_DIR, filename)

def resolve_output_path(output, project_name, file_type):
    """
    Resolve the output path for exported files.
    
    This ensures all exports go to the correct directory unless an absolute path is specified.
    
    Args:
        output: User-specified output path or None
        project_name: Name of the project or job ID to use in the filename
        file_type: Type of export (e.g., openpra, saphire, export)
        
    Returns:
        str: Resolved output path
    """
    # Ensure exports directory exists
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    if output:
        # If output is an absolute path, use it directly
        # Otherwise, place it in the exports directory
        if os.path.isabs(output):
            return output
        else:
            return os.path.join(EXPORTS_DIR, output)
    else:
        # Generate timestamped filename
        return get_timestamped_filename(project_name, file_type)

def resolve_job_id(job_id):
    """
    Resolve job ID, allowing '-' or 'last' to refer to the most recent job.
    
    Args:
        job_id: Job ID string or special value
        
    Returns:
        str: Resolved job ID
    """
    if job_id in ['-', 'last']:
        # Get most recent job
        all_jobs = db.get_all_jobs()
        if not all_jobs:
            raise ValueError("No jobs found")
        return all_jobs[0].get('id')
    return job_id

class AliasedGroup(click.Group):
    """Group with support for command aliases."""
    
    def __init__(self, *args, **kwargs):
        self.aliases = {}
        super(AliasedGroup, self).__init__(*args, **kwargs)
    
    def add_alias(self, alias, cmd_name):
        """Add an alias for a command."""
        self.aliases[alias] = cmd_name
        # For debugging
        logger.debug(f"Added alias '{alias}' for command '{cmd_name}'")
    
    def get_command(self, ctx, cmd_name):
        """Get a command by name, supporting aliases."""
        # Try to get the actual command
        cmd = super(AliasedGroup, self).get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd
        
        # Check if it's an alias
        if cmd_name in self.aliases:
            real_cmd = self.aliases[cmd_name]
            # For debugging
            logger.debug(f"Using alias: {cmd_name} -> {real_cmd}")
            return super(AliasedGroup, self).get_command(ctx, real_cmd)
        
        return None
    
    def resolve_command(self, ctx, args):
        # Get the original command resolution
        cmd_name = args[0] if args else ''
        
        # Try to get the command and fall back to alias
        cmd = self.get_command(ctx, cmd_name)
        
        # If command is not found but we have an alias for it
        if cmd is None and cmd_name in self.aliases:
            # Replace the command name with the aliased command in args
            args = [self.aliases[cmd_name]] + args[1:]
            return super(AliasedGroup, self).resolve_command(ctx, args)
            
        # Fall back to the default behavior
        cmd_name, cmd, args = super(AliasedGroup, self).resolve_command(ctx, args)
        
        return cmd_name, cmd, args

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(VERSION, '-v', '--version', message='%(version)s')
def cli():
    """Vyom: Nuclear LMP Safety Case Acceleration using PRA
    
    Vyom is a tool for processing SAPHIRE models and converting them to OpenPRA format.
    
    Basic usage:
      vyom import <zip_file>                          # Import SAPHIRE ZIP file
      vyom list                                       # List all jobs
      vyom explore <job_id> [--export] [--output=<file>] # Explore data, optionally export
      vyom convert <job_id> [--output=<file>]         # Convert to OpenPRA format
      vyom convert-file <input_file> [--output=<file>]# Convert a SAPHIRE JSON file directly
      vyom view <job_id>                              # Visualize in browser

    Use '-' or 'last' as job_id to refer to the most recent job.
    """
    pass

@cli.command(name='import', short_help="Import a zip folder containing SAPHIRE models")
@click.argument('zip_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output directory', default=None)
def import_(zip_file, output):
    """Import a zip folder containing SAPHIRE models.
    
    This command takes a ZIP file containing SAPHIRE model files, extracts them,
    analyzes their contents, and stores the results in a local database.
    
    Examples:
      vyom import path/to/saphire.zip
      vyom import path/to/saphire.zip --output path/to/extract
    """
    job_id = str(int(time.time()))
    click.echo(f"Starting import job {job_id}...")
    
    # Track job status in DB
    db.create_job(job_id, zip_file)
    
    try:
        # Extract and analyze zip contents
        extract_dir = extractor.extract_zip(zip_file, output_dir=output)
        click.echo(f"Extracted contents to {extract_dir}")
        
        # Process files and generate schema
        schema_data = extractor.analyze_files(extract_dir, job_id)
        
        # Save the schema data to the job_data table
        db.save_job_data(job_id, schema_data)
        
        # Update job status
        db.update_job_status(job_id, "COMPLETED", schema_data)
        
        # Report results
        total_files = schema_data.get("metadata", {}).get("total_files", 0)
        errors = schema_data.get("metadata", {}).get("errors", 0)
        warnings = schema_data.get("metadata", {}).get("warnings", 0)
        
        click.echo(f"Successfully processed {total_files} files")
        
        if errors:
            click.echo(f"Encountered {errors} errors")
        
        if warnings:
            click.echo(f"Encountered {warnings} warnings")
        
        # Check if SAPHIRE data was found and parsed
        if schema_data.get("saphire_data"):
            saphire_data = schema_data["saphire_data"]
            ft_count = len(saphire_data.get("fault_trees", []))
            et_count = len(saphire_data.get("event_trees", []))
            be_count = len(saphire_data.get("basic_events", []))
            es_count = len(saphire_data.get("end_states", []))
            seq_count = len(saphire_data.get("sequences", []))
            
            click.echo(f"Found SAPHIRE data:")
            click.echo(f"  Project: {saphire_data.get('project', {}).get('name', 'Unknown')}")
            click.echo(f"  {ft_count} Fault Trees")
            click.echo(f"  {et_count} Event Trees")
            click.echo(f"  {be_count} Basic Events")
            click.echo(f"  {es_count} End States")
            click.echo(f"  {seq_count} Sequences")
            
            # Generate detailed report of file types found
            file_types_count = {}
            for file_path, file_info in schema_data.get("files", {}).items():
                file_type = file_info.get("type", "unknown")
                file_types_count[file_type] = file_types_count.get(file_type, 0) + 1
            
            if file_types_count:
                click.echo("\nDetailed File Type Report:")
                for file_type, count in sorted(file_types_count.items()):
                    click.echo(f"  {file_type}: {count} files")
                
                # Check if sequences were found but no event trees (common case)
                if seq_count > 0 and et_count == 0:
                    click.echo("\nNote: Sequences were found but no event trees.")
                    click.echo("  This is normal for SAPHIRE exports that only contain sequence information.")
        else:
            click.echo("No SAPHIRE data found or parsed in the files")
        
        click.echo(f"\nJob ID: {job_id} - Use this ID for further operations")
        
        # Provide guidance on next steps
        click.echo("\n" + "=" * 60)
        click.echo("SUCCESS: Data imported and parsed into structured format")
        click.echo("=" * 60)
        click.echo("\nThe SAPHIRE data has been successfully imported and parsed according to")
        click.echo("the schema defined in vyom/schema/saphire_schema.json.")
        
        # Suggest next steps based on what was found
        click.echo("\nNext steps you can take:")
        
        # Always show explore option
        click.echo(f"  1. Explore the data structure:")
        click.echo(f"     vyom explore {job_id}")
        
        # Show export option
        click.echo(f"  2. Export the parsed data to JSON:")
        click.echo(f"     vyom explore {job_id} --export -o your_filename.json")
        
        # Visualization option is always available
        click.echo(f"  3. Visualize the data in a browser:")
        click.echo(f"     vyom view {job_id}")
        
        # Convert to OpenPRA if SAPHIRE data was found
        if schema_data.get("saphire_data"):
            click.echo(f"  4. Convert to OpenPRA format:")
            click.echo(f"     vyom convert {job_id} -o openpra_output.json")
        
    except Exception as e:
        db.update_job_status(job_id, "FAILED", {"error": str(e)})
        click.echo(f"Error processing zip: {str(e)}")
        logger.exception("Error processing ZIP file")

@cli.command(short_help="Explore and analyze SAPHIRE data")
@click.argument('job_id')
@click.option('--export', '-e', is_flag=True, help='Export the data to a file')
@click.option('--output', '-o', help='Output file path')
@click.option('--pretty/--compact', default=True, help='Pretty-print the output JSON')
@click.option('--format', '-f', help='Output format (default: json)', default='json', type=click.Choice(['json']))
@click.option('--query', '-q', help='JSON path query to filter data')
@click.option('--schema-info', '-s', is_flag=True, help='Display SAPHIRE schema information')
def explore(job_id, export, output, pretty, format, query, schema_info):
    """Explore and analyze SAPHIRE data from a job.
    
    This command provides a comprehensive view of the SAPHIRE data, including:
    - Job status and metadata
    - SAPHIRE data summary (fault trees, event trees, etc.)
    - File type breakdown
    - Sequence information
    
    The data can be filtered using JSONPath queries and optionally exported to a file.
    Use --schema-info to display information about the data schema structure.
    
    Examples:
      vyom explore 1679225432                    # Show job details
      vyom explore last --export                 # Export most recent job
      vyom explore - --output data.json          # Export to specific file
      vyom explore 1679225432 --query '$.files.*.type'  # Filter with JSONPath
      vyom explore 1679225432 --schema-info      # Show schema structure
    """
    try:
        job_id = resolve_job_id(job_id)
        job_data = db.get_job_data(job_id)
        if not job_data:
            click.echo(f"No data found for job {job_id}")
            return
        
        # Display schema information if requested
        if schema_info:
            schema_version = job_data.get("saphire_data", {}).get("version", "unknown")
            click.echo(f"SAPHIRE Schema Information (Version: {schema_version})")
            click.echo("=" * 60)
            click.echo("The following data structures are available in the parsed SAPHIRE data:")
            click.echo("\nMain Structure:")
            click.echo("  - project: Project information (name, description)")
            click.echo("  - fault_trees: Collection of fault tree objects")
            click.echo("  - event_trees: Collection of event tree objects")
            click.echo("  - basic_events: Collection of basic event objects")
            click.echo("  - end_states: Collection of end state objects")
            click.echo("  - sequences: Collection of sequence objects")
            
            click.echo("\nFault Tree Structure:")
            click.echo("  - id: Unique identifier")
            click.echo("  - name: Display name")
            click.echo("  - gates: Collection of gate objects (id, type, inputs)")
            click.echo("  - basic_events: List of basic events referenced in the tree")
            
            click.echo("\nEvent Tree Structure:")
            click.echo("  - id: Unique identifier")
            click.echo("  - name: Display name")
            click.echo("  - initiating_event: Reference to initiating event")
            click.echo("  - sequences: Collection of sequence path objects")
            click.echo("  - top_events: Collection of top event objects")
            
            click.echo("\nBasic Event Structure:")
            click.echo("  - id: Unique identifier")
            click.echo("  - name: Display name")
            click.echo("  - probability: Failure probability value")
            click.echo("  - description: Optional description")
            
            click.echo("\nExample query to access fault trees:")
            click.echo("  vyom explore job_id --query '$.saphire_data.fault_trees'")
            
            # Provide JSON Path tips
            click.echo("\nJSONPath Query Examples:")
            click.echo("  - List all file types:")
            click.echo("    $.files.*.type")
            click.echo("  - Get project name:")
            click.echo("    $.saphire_data.project.name")
            click.echo("  - List all sequence IDs:")
            click.echo("    $.saphire_data.sequences[*].id")
            
            click.echo("\nFor full schema details, see:")
            click.echo("  vyom/schema/saphire_schema.json")
            
            return
        
        # Get job status
        job = db.get_job(job_id)
        if not job:
            click.echo(f"Error: Job {job_id} not found")
            return
            
        status = job.get('status', 'UNKNOWN')
        source_path = job.get('source_path', 'Unknown')
        
        # Display job status
        click.echo(f"Job ID: {job_id}")
        click.echo(f"Status: {status}")
        click.echo(f"Source: {source_path}")
        click.echo()
        
        # Display SAPHIRE data summary
        if "saphire_data" in job_data:
            saphire_data = job_data["saphire_data"]
            ft_count = len(saphire_data.get("fault_trees", []))
            et_count = len(saphire_data.get("event_trees", []))
            be_count = len(saphire_data.get("basic_events", []))
            es_count = len(saphire_data.get("end_states", []))
            seq_count = len(saphire_data.get("sequences", []))
            
            click.echo("SAPHIRE Data Summary:")
            click.echo(f"  Project: {saphire_data.get('project', {}).get('name', 'Unknown')}")
            click.echo(f"  {ft_count} Fault Trees")
            click.echo(f"  {et_count} Event Trees")
            click.echo(f"  {be_count} Basic Events")
            click.echo(f"  {es_count} End States")
            click.echo(f"  {seq_count} Sequences")
            click.echo()
            
            # Generate detailed report of file types found
            file_types_count = {}
            for file_path, file_info in job_data.get("files", {}).items():
                file_type = file_info.get("type", "unknown")
                file_types_count[file_type] = file_types_count.get(file_type, 0) + 1
            
            if file_types_count:
                click.echo("Detailed File Type Report:")
                for file_type, count in sorted(file_types_count.items()):
                    click.echo(f"  {file_type}: {count} files")
                click.echo()
            
            # Show sequence information
            if seq_count > 0:
                click.echo("Sequence Information:")
                sequences = saphire_data.get("sequences", [])
                for seq in sequences[:5]:  # Show first 5 sequences
                    seq_id = seq.get("id", "Unknown")
                    description = seq.get("description", "No description")
                    click.echo(f"  {seq_id}: {description}")
                if seq_count > 5:
                    click.echo(f"  ... and {seq_count - 5} more sequences")
                click.echo()
            
            # Check if sequences were found but no event trees
            if seq_count > 0 and et_count == 0:
                click.echo("Note: Sequences were found but no event trees.")
                click.echo("  This is normal for SAPHIRE exports that only contain sequence information.")
                
            # Provide hint about schema info
            click.echo("\nTip: Run 'vyom explore job_id --schema-info' to see the data schema structure.")
        else:
            click.echo("No SAPHIRE data found or parsed in the files")
        
        # Handle export if requested
        if export:
            try:
                # Get project name if available, otherwise use job_id
                project_name = job_id
                if "saphire_data" in job_data and "project" in job_data["saphire_data"]:
                    project_name = job_data["saphire_data"]["project"].get("name", job_id)
                
                # Determine output path
                output_path = resolve_output_path(output, project_name, "export")
                
                # Write data to file
                indent = 2 if pretty else None
                with open(output_path, 'w') as f:
                    json.dump(job_data, f, indent=indent)
                
                click.echo(f"Raw data exported to {output_path}")
                
            except Exception as e:
                click.echo(f"Error exporting data: {str(e)}")
                logger.exception("Error exporting data")
                
    except ValueError as e:
        click.echo(f"Error: {str(e)}")

@cli.command(short_help="Convert extracted data to OpenPRA format")
@click.argument('job_id')
@click.option('--output', '-o', help='Output file path')
@click.option('--pretty/--compact', default=True, help='Pretty-print the output JSON')
@click.option('--format', '-f', help='Output format (default: json)', default='json', type=click.Choice(['json']))
def convert(job_id, output, pretty, format):
    """Convert extracted data to OpenPRA format.
    
    This command takes the extracted and processed data from a job and converts it
    to the OpenPRA schema format, saving the result to a file.
    
    Examples:
      vyom convert 1679225432
      vyom convert last --output openpra_result.json
      vyom convert - --compact  # Save as compact JSON
    """
    try:
        job_id = resolve_job_id(job_id)
        job_data = db.get_job_data(job_id)
        if not job_data:
            click.echo(f"No data found for job {job_id}")
            return
        
        try:
            click.echo(f"Converting job {job_id} to OpenPRA format...")
            openpra_data = converter.to_openpra(job_data)
            
            # Validate the data
            is_valid, message = openpra.validate_schema(openpra_data)
            if not is_valid:
                click.echo(f"Warning: Generated OpenPRA data may not be valid: {message}")
            
            # Get project name if available, otherwise use job_id
            project_name = job_id
            if "saphire_data" in job_data and "project" in job_data["saphire_data"]:
                project_name = job_data["saphire_data"]["project"].get("name", job_id)
                
            # Determine output path
            output_path = resolve_output_path(output, project_name, "openpra")
            
            # Write data to file
            indent = 2 if pretty else None
            with open(output_path, 'w') as f:
                json.dump(openpra_data, f, indent=indent)
            
            # Save conversion info to DB
            db.save_conversion(job_id, "openpra", output_path)
            
            # Report results
            ft_count = len(openpra_data.get("models", {}).get("fault_trees", []))
            et_count = len(openpra_data.get("models", {}).get("event_trees", []))
            be_count = len(openpra_data.get("models", {}).get("basic_events", []))
            es_count = len(openpra_data.get("models", {}).get("end_states", []))
            
            click.echo(f"Converted data saved to {output_path}")
            click.echo(f"OpenPRA model contains:")
            click.echo(f"  {ft_count} Fault Trees")
            click.echo(f"  {et_count} Event Trees")
            click.echo(f"  {be_count} Basic Events")
            click.echo(f"  {es_count} End States")
            
        except Exception as e:
            click.echo(f"Error converting data: {str(e)}")
            logger.exception("Error converting to OpenPRA format")
    except ValueError as e:
        click.echo(f"Error: {str(e)}")

@cli.command(short_help="Convert a SAPHIRE JSON file directly to OpenPRA")
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--pretty/--compact', default=True, help='Pretty-print the output JSON')
@click.option('--format', '-f', help='Output format (default: json)', default='json', type=click.Choice(['json']))
def convert_file(input_file, output, pretty, format):
    """Convert a SAPHIRE JSON file directly to OpenPRA format.
    
    This command takes a JSON file containing SAPHIRE schema data and converts
    it to the OpenPRA schema format without requiring a job.
    
    Examples:
      vyom convert-file saphire_data.json
      vyom convert-file saphire_data.json --output openpra_result.json
    """
    try:
        # Load the SAPHIRE file
        click.echo(f"Loading SAPHIRE data from {input_file}...")
        with open(input_file, 'r') as f:
            saphire_data = json.load(f)
        
        # Convert to OpenPRA
        click.echo("Converting to OpenPRA format...")
        openpra_data = converter.to_openpra(saphire_data)
        
        # Validate the data
        is_valid, message = openpra.validate_schema(openpra_data)
        if not is_valid:
            click.echo(f"Warning: Generated OpenPRA data may not be valid: {message}")
        
        # Extract project name from file if available, otherwise use filename
        project_name = os.path.splitext(os.path.basename(input_file))[0]
        if "project" in saphire_data and "name" in saphire_data["project"]:
            project_name = saphire_data["project"]["name"]
        
        # Determine output path
        output_path = resolve_output_path(output, project_name, "openpra")
        
        # Write data to file
        indent = 2 if pretty else None
        with open(output_path, 'w') as f:
            json.dump(openpra_data, f, indent=indent)
        
        # Report results
        ft_count = len(openpra_data.get("models", {}).get("fault_trees", []))
        et_count = len(openpra_data.get("models", {}).get("event_trees", []))
        be_count = len(openpra_data.get("models", {}).get("basic_events", []))
        es_count = len(openpra_data.get("models", {}).get("end_states", []))
        
        click.echo(f"Converted data saved to {output_path}")
        click.echo(f"OpenPRA model contains:")
        click.echo(f"  {ft_count} Fault Trees")
        click.echo(f"  {et_count} Event Trees")
        click.echo(f"  {be_count} Basic Events")
        click.echo(f"  {es_count} End States")
        
    except json.JSONDecodeError:
        click.echo(f"Error: {input_file} is not a valid JSON file")
    except Exception as e:
        click.echo(f"Error converting file: {str(e)}")
        logger.exception("Error converting file to OpenPRA format")

@cli.command(short_help="List all jobs with their status")
def list():
    """List all jobs with their status.
    
    This command displays a list of all jobs in the database, showing their
    ID, status, and source path.
    
    Examples:
      vyom list
    """
    all_jobs = db.get_all_jobs()
    if not all_jobs:
        click.echo("No jobs found")
        return
    
    click.echo(f"Found {len(all_jobs)} jobs:")
    for job in all_jobs:
        status_color = {
            "COMPLETED": "green",
            "PROCESSING": "yellow",
            "FAILED": "red"
        }.get(job.get("status"), "white")
        
        click.echo(f"{job.get('id')}: "
                 f"{click.style(job.get('status', 'UNKNOWN'), fg=status_color)} - "
                 f"{job.get('source_path', 'Unknown source')}")

@cli.command(short_help="Visualize SAPHIRE data or generate visualizations")
@click.argument('job_id', required=False)
@click.option('--no-browser', is_flag=True, help="Don't open visualization in browser")
@click.option('--use-llm/--no-llm', default=None, help="Use LLM for enhanced visualization (default: use environment setting)")
@click.option('--prompt', help="Natural language prompt to customize visualization")
@click.option('--data-file', type=click.Path(exists=True), help="JSON data file to use (instead of job_id)")
@click.option('--output-dir', type=click.Path(), default='data/visual',
              help='Directory to save visualization files')
@click.option('--web', is_flag=True, help="Start interactive web server mode")
@click.option('--port', type=int, default=8000, help="Port for web server (when using --web)")
@click.option('--llm-service', type=click.Choice(['together', 'brave']), help="LLM service to use")
@click.option('--legacy', is_flag=True, help="Use legacy visualization format")
@click.option('--verbose', is_flag=True, help="Show detailed processing information")
def view(job_id, no_browser, use_llm, prompt, data_file, output_dir, web, port, llm_service, legacy, verbose):
    """Visualize SAPHIRE data or generate visualizations.
    
    If JOB_ID is provided, visualizes data from that job.
    Otherwise, can generate visualizations from prompts or data files.
    """
    # Set verbose mode in environment if specified
    if verbose:
        os.environ["VERBOSE_LLM"] = "1"
        click.echo("Verbose mode enabled - showing detailed processing information")
    
    # Configure LLM service if specified
    if llm_service:
        os.environ["LLM_SERVICE"] = llm_service
        click.echo(f"Using LLM service: {llm_service}")
    
    # Configure LLM usage based on options
    if use_llm is not None:
        os.environ["USE_LLM"] = "true" if use_llm else "false"
        if use_llm:
            # Check prerequisites for use-llm command
            if not session.check_command_prerequisites('use-llm'):
                click.echo("Error: --use-llm flag requires --no-llm to be executed first")
                click.echo("Please run the command with --no-llm first")
                return
            click.echo("Using LLM for enhanced visualization")
        else:
            click.echo("Using rule-based visualization (LLM disabled)")
    
    # WEB SERVER MODE
    if web:
        click.echo(f"Starting web visualization server on port {port}...")
        try:
            # Simple HTTP server with WSGI app
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import urllib.parse
            import html
            
            class VisualizationHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        form_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>AI Visualization Generator</title>
                            <style>
                                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
                                .container {{ max-width: 800px; margin: 0 auto; }}
                                h1 {{ color: #2c3e50; }}
                                .form-group {{ margin-bottom: 15px; }}
                                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                                input, textarea {{ width: 100%; padding: 8px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; }}
                                textarea {{ height: 100px; }}
                                button {{ background: #3498db; color: white; border: none; padding: 10px 15px; font-size: 16px; border-radius: 4px; cursor: pointer; }}
                                button:hover {{ background: #2980b9; }}
                                .setting {{ font-size: 14px; color: #666; margin: 20px 0; }}
                                .setting span {{ font-weight: bold; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>AI Visualization Generator</h1>
                                <div class="setting">LLM Processing: <span>{use_llm}</span> | Service: <span>{llm_service}</span></div>
                                <form action="/generate" method="post">
                                    <div class="form-group">
                                        <label for="prompt">Describe the visualization you want:</label>
                                        <textarea id="prompt" name="prompt" required></textarea>
                                    </div>
                                    <button type="submit">Generate Visualization</button>
                                </form>
                            </div>
                        </body>
                        </html>
                        """
                        self.wfile.write(form_html.encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Not found')
                
                def do_POST(self):
                    if self.path == '/generate':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length).decode('utf-8')
                        params = urllib.parse.parse_qs(post_data)
                        
                        prompt = params.get('prompt', [''])[0]
                        
                        if prompt:
                            try:
                                html_content = viewer.handle_prompt(prompt)
                                
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                self.wfile.write(html_content.encode())
                            except Exception as e:
                                self.send_response(500)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                error_html = f"<h1>Error</h1><p>{html.escape(str(e))}</p>"
                                self.wfile.write(error_html.encode())
                        else:
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(b'<h1>Bad Request</h1><p>Missing prompt</p>')
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Not found')
            
            # Start the server
            server = HTTPServer(('localhost', port), VisualizationHandler)
            click.echo(f"Server started at http://localhost:{port}")
            click.echo("Press Ctrl+C to stop the server")
            
            # Open browser automatically
            import webbrowser
            webbrowser.open(f"http://localhost:{port}")
            
            # Run the server
            server.serve_forever()
        except KeyboardInterrupt:
            click.echo("\nShutting down server")
            server.socket.close()
        except Exception as e:
            click.echo(f"Error starting server: {e}")
        return
    
    # Load data from job_id if specified
    if job_id:
        try:
            resolved_job_id = resolve_job_id(job_id)
            click.echo(f"Creating visualization for job {resolved_job_id}...")
            data = db.get_job_data(resolved_job_id)
            if not data:
                click.echo(f"No data found for job {resolved_job_id}")
                return
        except ValueError as e:
            click.echo(f"Error: {str(e)}")
            return
    
    # Load data from file if specified
    elif data_file:
        click.echo(f"Creating visualization from file: {data_file}")
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            click.echo(f"Error loading data file: {str(e)}")
            return
    
    # PROMPT-ONLY MODE (former "generate" command)
    elif prompt and not job_id:
        click.echo(f"Generating visualization from prompt: {prompt}")
        try:
            output_dir = os.path.dirname(output_dir) if output_dir else "visual"
            output_path = viewer.handle_prompt(prompt, data, 
                                              output_dir=output_dir, browser=not no_browser)
            
            if no_browser:
                click.echo(f"Visualization created at {output_path}")
            else:
                click.echo(f"Visualization opened in browser. File saved at {output_path}")
            return
        except Exception as e:
            click.echo(f"Error generating visualization: {str(e)}")
            logger.exception("Error generating visualization")
            return
    
    # Error if no input source specified
    elif not job_id and not data_file and not web:
        click.echo("Error: You must specify a job_id, data-file, prompt, or --web flag")
        return
    
    # Track command execution
    command_name = 'no-llm' if use_llm is False else 'use-llm' if use_llm is True else 'view'
    session.track_command_execution(command_name, {'job_id': job_id, 'data_file': data_file})
    
    # VISUALIZATION GENERATION
    try:
        # Generate visualization
        if prompt:
            # If a natural language prompt is provided, use the LLM-enhanced handle_prompt
            click.echo(f"Applying prompt: {prompt}")
            click.echo("Stage 1: Creating data summary and visualization plan...")
            output_dir = os.path.dirname(output_dir) if output_dir else "visual"
            output_path = viewer.handle_prompt(prompt, data, 
                                              output_dir=output_dir, browser=not no_browser)
            click.echo("Stage 2: Generating visualization from plan...")
        else:
            # Otherwise use the traditional visualize_saphire_data
            output_dir = os.path.dirname(output_dir) if output_dir else "visual"
            if legacy:
                click.echo("Using legacy visualization format...")
            output_path = viewer.visualize_saphire_data(data, output_dir=output_dir,
                                                      browser=not no_browser,
                                                      use_legacy=legacy)
        
        if no_browser:
            click.echo(f"Visualization created at {output_path}")
            click.echo("To view it, open the file in your web browser")
        else:
            click.echo(f"Visualization opened in browser. File saved at {output_path}")
        
    except Exception as e:
        click.echo(f"Error creating visualization: {str(e)}")
        logger.exception("Error creating visualization")

# Add a simple web server command to view visualizations
# @cli.command(short_help="Start a web server for interactive visualization")
# @click.option('--port', type=int, default=8000, help="Port to run the server on")
# @click.option('--use-llm/--no-llm', default=True, help="Enable/disable LLM for processing")
# @click.option('--llm-service', type=click.Choice(['together', 'brave']), help="LLM service to use")
# def web(port, use_llm, llm_service):
#     """Start a web server for interactive visualization generation.
#     
#     This launches a simple web server that provides an interface for entering
#     prompts and generating visualizations. The server runs locally and can be
#     accessed through your web browser.
#     
#     Examples:   vyom web   vyom web --port 8080   vyom web --no-llm
#     """

# Add command aliases
cli.add_alias('i', 'import')
cli.add_alias('l', 'list')
cli.add_alias('e', 'explore')
cli.add_alias('c', 'convert')
cli.add_alias('cf', 'convert-file')
cli.add_alias('v', 'view')

# For backward compatibility (temporary)
# These will be removed in a future version
cli.add_alias('process', 'import')
cli.add_alias('jobs', 'list')
cli.add_alias('status', 'show')
cli.add_alias('visualize', 'view')

if __name__ == '__main__':
    cli()
