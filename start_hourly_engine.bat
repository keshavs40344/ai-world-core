@echo off
title Genesis Hourly Agent Crucible
echo ===================================================
echo Starting Autonomous Hourly Agent Crucible Daemon...
echo Target Cycle Interval: 3600 seconds
echo ===================================================

python hourly_agent_crucible.py --interval 3600
pause
