"""
Ingestion Service - Processes files from Redis queue and moves to Logstash
Listens to Redis list 'ingest_jobs', moves files to Logstash watch directory,
and logs status updates to MongoDB.
"""

import os
import shutil
import time
import logging
import json
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service that processes file ingestion jobs from Redis queue
    """
    
    def __init__(self, redis_service, mongo_service, 
                 source_dir: str = './uploads',
                 target_dir: str = './uploads',
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 poll_interval: int = 5):
        """
        Initialize ingestion service
        
        Args:
            redis_service: Redis service instance
            mongo_service: MongoDB service instance
            source_dir: Source directory for uploaded files
            target_dir: Target directory (Logstash watch directory)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            poll_interval: Queue polling interval in seconds
        """
        self.redis_service = redis_service
        self.mongo_service = mongo_service
        self.source_dir = Path(source_dir).resolve()
        self.target_dir = Path(target_dir).resolve()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.poll_interval = poll_interval
        self.running = False
        
        # Create directories if they don't exist
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Ingestion Service initialized")
        logger.info(f"Source directory: {self.source_dir}")
        logger.info(f"Target directory: {self.target_dir}")
        logger.info(f"Max retries: {max_retries}, Retry delay: {retry_delay}s")
    
    def update_job_status(self, job_id: str, status: str, 
                         error_message: Optional[str] = None,
                         retry_count: int = 0) -> bool:
        """
        Update job status in MongoDB
        
        Args:
            job_id: Job ID
            status: Status (pending, processing, completed, failed)
            error_message: Error message if failed
            retry_count: Number of retry attempts
        
        Returns:
            bool: Success status
        """
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow(),
                'retry_count': retry_count
            }
            
            if error_message:
                update_data['error_message'] = error_message
            
            if status == 'completed':
                update_data['processed'] = True
                update_data['completed_at'] = datetime.utcnow()
            elif status == 'failed':
                update_data['processed'] = False
                update_data['failed_at'] = datetime.utcnow()
            
            # Update in MongoDB 'uploads' collection
            result = self.mongo_service.update_one(
                'uploads',
                {'job_id': job_id},
                {'$set': update_data}
            )
            
            logger.info(f"Job {job_id} status updated to '{status}'")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update job status: {str(e)}", exc_info=True)
            return False
    
    def move_file_to_logstash(self, source_path: str, file_type: str) -> bool:
        """
        Move file to Logstash watch directory
        
        Args:
            source_path: Source file path
            file_type: File type (csv, json)
        
        Returns:
            bool: Success status
        """
        try:
            source = Path(source_path)
            
            # Check if source file exists
            if not source.exists():
                logger.error(f"Source file does not exist: {source_path}")
                return False
            
            # Target path (same directory since both use ./uploads)
            target = self.target_dir / source.name
            
            # If source and target are the same directory, file is already in place
            if source.parent.resolve() == self.target_dir:
                logger.info(f"File already in Logstash watch directory: {source.name}")
                return True
            
            # Move file to target directory
            shutil.move(str(source), str(target))
            logger.info(f"Moved file to Logstash watch directory: {source.name} -> {target}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file: {str(e)}", exc_info=True)
            return False
    
    def process_job(self, job_data: Dict) -> bool:
        """
        Process a single ingestion job with retry logic
        
        Args:
            job_data: Job data dictionary
        
        Returns:
            bool: Success status
        """
        job_id = job_data.get('job_id')
        file_path = job_data.get('file_path')
        file_type = job_data.get('file_type')
        
        logger.info(f"Processing job {job_id}: {file_path}")
        
        # Update status to processing
        self.update_job_status(job_id, 'processing')
        
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                # Move file to Logstash watch directory
                success = self.move_file_to_logstash(file_path, file_type)
                
                if success:
                    # Update status to completed
                    self.update_job_status(job_id, 'completed')
                    logger.info(f"Job {job_id} completed successfully")
                    return True
                else:
                    raise Exception("Failed to move file to Logstash directory")
                
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                logger.warning(f"Job {job_id} attempt {retry_count}/{self.max_retries} failed: {last_error}")
                
                if retry_count < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    # Max retries reached, mark as failed
                    self.update_job_status(
                        job_id, 
                        'failed', 
                        error_message=f"Max retries exceeded: {last_error}",
                        retry_count=retry_count
                    )
                    logger.error(f"Job {job_id} failed after {retry_count} attempts")
                    return False
        
        return False
    
    def listen_and_process(self):
        """
        Main loop - Listen to Redis queue and process jobs
        """
        logger.info("Starting ingestion service listener...")
        self.running = True
        
        while self.running:
            try:
                # Check queue length
                queue_length = self.redis_service.llen('ingest_jobs')
                
                if queue_length > 0:
                    logger.info(f"Found {queue_length} jobs in queue")
                    
                    # Pop job from queue (FIFO - right side)
                    job_data_raw = self.redis_service.rpop('ingest_jobs')
                    
                    if job_data_raw:
                        try:
                            # Parse job data
                            if isinstance(job_data_raw, str):
                                job_data = json.loads(job_data_raw)
                            else:
                                job_data = job_data_raw
                            
                            # Process the job
                            self.process_job(job_data)
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid job data in queue: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error processing job: {str(e)}", exc_info=True)
                else:
                    # No jobs, wait before checking again
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                time.sleep(self.poll_interval)
        
        logger.info("Ingestion service stopped")
    
    def stop(self):
        """Stop the service gracefully"""
        logger.info("Stopping ingestion service...")
        self.running = False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def main():
    """Main entry point for ingestion service"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Import services
    from app.services.redis_service import RedisService
    from app.services.mongodb_service import MongoDBService
    from config import get_config
    
    try:
        # Load configuration
        config = get_config()
        
        # Initialize services
        logger.info("Initializing services...")
        redis_service = RedisService(config.REDIS_CONFIG)
        mongo_service = MongoDBService(config.MONGODB_CONFIG)
        
        # Create ingestion service
        ingestion_service = IngestionService(
            redis_service=redis_service,
            mongo_service=mongo_service,
            source_dir='./uploads',
            target_dir='./uploads',  # Same directory - Logstash watches ./uploads
            max_retries=3,
            retry_delay=5,
            poll_interval=5
        )
        
        # Start listening and processing
        ingestion_service.listen_and_process()
        
    except Exception as e:
        logger.error(f"Failed to start ingestion service: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
