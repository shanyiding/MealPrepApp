# MealPrep App

## Overview

MealPrep is a personal mobile application designed to help users manage their food inventory, track nutritional intake, and maintain accountability during fitness goals such as cutting or bulking.

The application is being developed primarily for Android using **Python**, **Kivy**, and **SQLite**.

The main purpose of the app is to answer questions such as:

* What food do I currently have in my fridge?
* How much protein and calories do I have available?
* How long can my current groceries sustain my goals?
* What have I eaten today?
* Am I staying within my calorie and protein targets?

---

## Tech Stack

### Frontend

* Python
* Kivy

### Backend

* Python

### Database

* SQLite

### Development Environment

* VS Code
* Windows 11

---

## Current Features (Implemented)

### Fridge Inventory Management

Users can view all current food items stored in their fridge.

Each inventory item displays:

* Food name
* Quantity remaining
* Unit (g, piece, ml, etc.)
* Total calories available
* Total protein available
* Purchase batch information and dates

Example:

```text
Lean Ground Beef
Amount: 900 g
Calories stored: 1530 kcal
Protein stored: 207 g

Batches:
2026-06-01: 500 g
2026-06-06: 400 g
```

---

### Add Grocery

Users can add groceries into inventory.

Supports:

* Creating completely new ingredients
* Adding additional quantities to existing ingredients
* Maintaining separate purchase batches and purchase dates

Example:

Current inventory:

```text
Eggs: 10
```

Purchase:

```text
100 eggs
Date: 2026-06-07
```

Inventory becomes:

```text
Eggs: 110

Batches:
2026-06-01: 10 eggs
2026-06-07: 100 eggs
```

---

### Remove / Throw Out Food

Users can deduct quantities from inventory without manually recalculating nutrition.

Supports:

* Throwing away spoiled food
* Removing food accidentally logged incorrectly

Inventory deduction follows FIFO (First-In-First-Out):

Oldest batches are consumed first.

Example:

Inventory:

```text
500 g beef (June 1)
400 g beef (June 6)
```

Remove:

```text
600 g beef
```

Remaining:

```text
0 g beef (June 1)
300 g beef (June 6)
```

---

### Fridge Summary

Displays overall nutritional availability within the fridge.

Current metrics:

* Total calories available
* Total protein available
* Number of unique food items

Example:

```text
Fridge Summary

🔥 Total Calories: 14,520 kcal

💪 Total Protein: 1,280 g

📦 Foods: 8
```

---

### Collapsible Cards

The following sections support collapsing:

* Add Grocery
* Remove / Throw Out

This allows users to focus primarily on viewing fridge contents.

---

## Project Structure

```text
MealPrepApp/

├── main.py
├── database.py
├── mealprep.db

├── screens/
│   ├── __init__.py
│   └── fridge_page.py

├── ui/
│   ├── __init__.py
│   └── fridge_ui.py
```

### Responsibilities

#### main.py

* Application entry point
* Initializes database
* Launches the fridge page

#### database.py

Handles:

* Database initialization
* Ingredient management
* Inventory management
* Batch tracking
* Inventory deductions
* Summary calculations

#### screens/fridge_page.py

Handles:

* Business logic
* Connecting database operations with UI actions

#### ui/fridge_ui.py

Handles:

* User interface layout
* Buttons
* Forms
* Inventory display
* Summary display

---

## Planned Features

### Meal Logging

Users will be able to:

* Record foods eaten
* Specify quantity consumed
* Automatically deduct inventory
* Automatically calculate nutritional intake

Example:

```text
225 g Ground Beef
120 g Greek Yogurt
3 Eggs
```

Automatically updates:

* Daily calories
* Daily protein
* Daily fiber
* Food inventory

---

### Daily Dashboard

Displays:

```text
Calories:
1500 / 1700 kcal

Protein:
125 / 130 g

Fiber:
22 / 25 g
```

---

### Cost Tracking

Each food purchase will include price information.

The application will calculate:

* Cost per gram
* Daily food expenditure
* Monthly food spending trends

---

### Sustainability Estimates

Estimate how long current groceries will sustain nutritional goals.

Example:

```text
Current inventory supports:

Calories:
8.4 days

Protein:
10.1 days
```

---

### Weight Tracking

Future integration:

```text
Date       Weight
2026-06-01 68.0 kg
2026-06-08 67.2 kg
```

Used to monitor progress during cuts or bulks.

---

## Motivation

This application was created to solve common problems encountered during meal prepping:

* Forgetting what food is available
* Buying duplicate groceries unnecessarily
* Losing track of calories and protein intake
* Difficulty maintaining accountability during dieting phases
* Understanding how long current food supplies will last

The goal is to provide a simple but powerful tool that combines:

* Inventory management
* Nutrition tracking
* Budget awareness
* Fitness accountability

into one application.
