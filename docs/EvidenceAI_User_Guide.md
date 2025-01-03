# EvidenceAI User Guide

## Introduction

EvidenceAI is a tool designed to help analyze Our Family Wizard (OFW) communications. It takes your OFW PDF exports and transforms them into organized, enriched data that can be analyzed by various AI tools, while carefully preserving all context and relationships between messages.

## Step-by-Step Instructions

### Step 1: Preparing Your Files

Before starting your analysis:
1. Export your communications from Our Family Wizard as a PDF
2. Create a folder called "input" in your EvidenceAI directory
3. Place your PDF file into this input folder
4. Make sure you have permission to read and write to these folders

### Step 2: Running the Analysis

You have two options for running the analysis:

**Option 1: Using the Simple Method (Recommended)**
1. Find the file named "run_analysis.bat" in your EvidenceAI folder
2. Double-click this file to start
3. When prompted, choose "Start Fresh" 
4. Wait for the "Analysis Complete" message

**Option 2: Using the Command Line**
1. Open Command Prompt
2. Navigate to your EvidenceAI folder
3. Type: python src/run_analysis.py
4. Press Enter and follow the prompts

### Step 3: Monitoring Your Analysis

While the analysis runs, you can track progress by:
- Watching the progress messages on your screen
- Checking the analysis.log file in the output folder
- Looking at checkpoint files as they're created

## Finding Your Results

### Where to Look

Your analysis results will be organized in folders:

**Main Output Folder Structure:**
- checkpoints folder: Contains results from each stage
- final folder: Contains your completed analysis
- analysis.log: Keeps track of what happened

**Important Files You'll Find:**
1. Messages and their details (messages.json)
2. How messages connect to each other (relationships.json)
3. Analysis of timing patterns (temporal_analysis.json)
4. Maps of who's talking to whom (interaction_maps.json)

## Using the Results

### Preparing for Analysis

The system organizes your data into three main areas:

1. **Message Content**
   - Use messages.json to see what was said
   - Use relationships.json to understand context

2. **Timing Analysis**
   - Use temporal_analysis.json to see when things happened
   - Look at date ranges to understand timeframes

3. **Communication Patterns**
   - Use interaction_maps.json to see how people communicate
   - Check metadata to understand who's involved

### Analysis Examples

When analyzing your data, consider asking questions like:

**For Communication Patterns:**
- When do people typically communicate?
- How quickly do they respond to each other?
- How do conversations develop over time?

**For Relationship Understanding:**
- Who talks to whom most often?
- How do response patterns change over time?
- How do different people interact?

## Best Practices

### Working with the Data

Always remember to:
1. Use complete data sets
2. Keep track of context
3. Reference original messages when needed
4. Start with big picture patterns
5. Look closer at specific conversations
6. Check how things connect
7. Stay objective

### Important Reminders

- The system organizes but doesn't interpret
- Original context is always kept
- You can look at the data in many ways
- Always verify findings against original messages

## Troubleshooting Guide

### Common Problems and Solutions

**If Files Are Missing:**
- Check that your files are in the right folders
- Make sure you have permission to use the folders
- Look at the analysis.log file for errors

**If Processing Stops Working:**
- Check the checkpoint files
- Read any error messages
- Try starting fresh

**If Analysis Looks Wrong:**
- Make sure all your data is there
- Check that files are in the right format
- Review how messages connect to each other

### Getting Help

If you need help:
1. First check the log files
2. Look at your checkpoint data
3. Make sure you can access all files
4. Read through the documentation

Remember: The system is designed to help you understand communication patterns while keeping everything in context. Take time to verify your findings and always reference back to the original messages when needed.