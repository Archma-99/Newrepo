import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

class Event(Base):
    """SQLAlchemy model for storing events."""
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50), index=True)
    source = Column(String(50))
    impact = Column(String(50))
    details = Column(Text) # Store details as a JSON string
    confidence = Column(Float)

    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', source='{self.source}')>"

class Database:
    """Handles all database operations."""
    def __init__(self, db_url: str):
        try:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection and tables initialized successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database at {db_url}: {e}")
            raise

    def add_event(self, event_data: dict):
        """Adds a new event to the database."""
        session = self.Session()
        try:
            event = Event(
                timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '')),
                event_type=event_data.get('type'),
                source=event_data.get('source'),
                impact=event_data.get('impact'),
                details=str(event_data.get('details', {})),
                confidence=event_data.get('confidence')
            )
            session.add(event)
            session.commit()
            logger.info(f"Successfully stored event: {event.event_type} from {event.source}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to add event to database: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_recent_events(self, timespan_seconds: int) -> list[Event]:
        """Retrieves events within a recent timespan."""
        session = self.Session()
        try:
            time_threshold = datetime.utcnow() - timedelta(seconds=timespan_seconds)
            events = session.query(Event).filter(Event.timestamp >= time_threshold).order_by(Event.timestamp.desc()).all()
            return events
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve recent events: {e}")
            return []
        finally:
            session.close()

    def cleanup_old_events(self, expiration_seconds: int):
        """Removes events older than the specified expiration time."""
        session = self.Session()
        try:
            time_threshold = datetime.utcnow() - timedelta(seconds=expiration_seconds)
            num_deleted = session.query(Event).filter(Event.timestamp < time_threshold).delete()
            session.commit()
            if num_deleted > 0:
                logger.info(f"Cleaned up {num_deleted} old events from the database.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to clean up old events: {e}")
            session.rollback()
        finally:
            session.close()