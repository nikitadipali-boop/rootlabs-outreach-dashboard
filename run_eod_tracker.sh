#!/bin/bash
# EOD Outreach Tracker Runner
# Runs daily_tracker.py --eod to lock today's scorecard row

cd ~/Desktop/apollo-analytics/airtable-visibility-tracker

/usr/bin/python3 daily_tracker.py --eod >> ~/Desktop/apollo-analytics/airtable-visibility-tracker/tracker.log 2>&1

# Send macOS notification
osascript -e 'display notification "EOD scorecard locked - check Historical Performance page" with title "RootLabs Outreach Tracker" sound name "Glass"'
