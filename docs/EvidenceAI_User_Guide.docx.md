EvidenceAI User Guide

QUICK REFERENCE GUIDE
--------------------

Quick Start:
1. Export your OFW data as PDF
2. Double-click run_analysis.bat
3. Choose "Start Fresh"
4. Wait for completion message

Key Folders (Created Automatically):
- input: Your PDF goes here
- output/final: Find your results here
- output/checkpoints: Progress tracking

Common Issues - Quick Fix:
- Analysis won't start → Check if PDF is present
- Error message → Check analysis.log
- Need to restart → Choose "Start Fresh"

Need Help? Check:
1. analysis.log in output folder
2. checkpoint files in output/checkpoints
3. documentation

--------------------

Introduction

EvidenceAI helps you understand and analyze Our Family Wizard (OFW) communications. It automatically handles all the technical setup and organization, letting you focus on understanding the communications patterns and relationships in your data.

Getting Started

Step 1: Prepare Your Files
1. Export your OFW communications as a PDF
2. Run the analysis tool once - it will create all needed folders
3. Put your PDF in the newly created "input" folder

Step 2: Start Your Analysis

Simple Method (Recommended):
1. Find and double-click run_analysis.bat
2. Choose "Start Fresh" when asked
3. Wait for "Analysis Complete"

Alternative Method:
1. Open Command Prompt
2. Go to your EvidenceAI folder
3. Type: python src/run_analysis.py
4. Follow the prompts

[Rest of content remains the same...]