#!/usr/bin/env python3
"""
Standalone scheduler service for auto-syncing packages.
Runs as a SEPARATE process from the Flask app (which may have multiple
gunicorn workers). This ensures auto-sync runs exactly once, avoiding
race conditions on tracking_number uniqueness.
"""
import logging
from dotenv import load_dotenv
load_dotenv()

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_auto_sync():
	"""Auto sync all active API keys with auto_sync enabled"""
	from app import create_app, sync_packages, cooldown_ok
	app = create_app()

	with app.app_context():
		from models import APIKey
		keys = APIKey.query.filter_by(is_active=True, auto_sync=True).all()

		if not keys:
			logger.info("No API keys with auto_sync enabled")
			return

		for key in keys:
			ok, msg = cooldown_ok(key)
			if ok:
				try:
					success, message = sync_packages(
						key, days=3, sync_type='auto', direction='both'
					)
					logger.info(f"Auto-synced: {key.label} - {message}")
				except Exception as e:
					logger.error(f"Failed to sync {key.label}: {e}")
			else:
				logger.info(f"Skipped {key.label}: {msg}")


def main():
	scheduler = BlockingScheduler()

	scheduler.add_job(
		run_auto_sync,
		'cron',
		hour='8-20',
		minute='*/30',
		timezone='Europe/Kyiv',
		id='auto_sync',
		replace_existing=True,
		misfire_grace_time=300
	)

	logger.info("✅ Scheduler service started - syncing every 30min (8:00-20:00 Kyiv time)")

	# Run once immediately on startup to verify everything works
	try:
		logger.info("Running initial sync on startup...")
		run_auto_sync()
	except Exception as e:
		logger.error(f"Initial sync failed: {e}")

	try:
		scheduler.start()
	except (KeyboardInterrupt, SystemExit):
		logger.info("Scheduler stopped")


if __name__ == '__main__':
	main()