# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Date: Sept 12, 2024
# Description: This is the main python file for an automated meeting summarizer application

import ActionableItems
import Minutes

# Retrieve file path from user
# Replace with UI method once developed
filepath = input("Enter name of transcript file: ")

# Generate minutes document and summary terminal output
Minutes.generateMinutes(filepath)

# Identify actionable items
ActionableItems.outputActionableItems(filepath)