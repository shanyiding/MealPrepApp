# MealPrep App

## Overview

MealPrep is a personal meal preparation and nutrition tracking application designed to help users manage their fridge inventory, monitor nutritional intake, and stay accountable to fitness goals such as cutting, bulking, or maintenance.

The app combines **food inventory management**, **nutrition tracking**, and **meal prep planning** into a single mobile-first experience.

Built primarily for Android using **Python**, **Kivy**, and **SQLite**, the app aims to answer questions such as:

* What food do I currently have in my fridge?
* How much protein and calories do I have available?
* Which foods are getting old and should be eaten soon?
* What foods fit my nutrition goals?
* Am I staying within my calorie and protein targets?
* What have I eaten today?
* How long can my current groceries sustain my goals?

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

## Fridge Inventory Management

Users can view all food items currently stored in their fridge.

Each inventory item displays:

* Food name
* Quantity remaining
* Unit (g, piece, ml, etc.)
* Total calories stored
* Total protein stored
* Food category tags
* Purchase batch information
* Freshness indicators

Example:

```text
Lean Ground Beef

900 g remaining

Cal 1530    Pro 207 g    Protein

5 days old
2026-06-01
2026-06-06
```

---

## Batch Tracking

The app tracks food by purchase batches.

When additional quantities of an existing ingredient are purchased:

* Quantities are merged into total inventory.
* Purchase dates are preserved.
* Multiple batches remain visible.

Example:

Current inventory:

```text
Eggs: 10
Purchased: 2026-06-01
```

New purchase:

```text
100 eggs
Purchased: 2026-06-07
```

Result:

```text
Eggs: 110

Batches:
2026-06-01
2026-06-07
```

---

## Add Grocery

Users can quickly add groceries using a mobile-optimized form.

### Fields

Row 1:

* Food Name
* Quantity
* Unit

Row 2:

* Calories (per unit)
* Protein (g/unit)
* Tag (dropdown)
* Date Purchased

Supported tags:

* Protein
* Fibre
* Carbs
* Others

Features:

* Create completely new ingredients
* Add additional quantities to existing ingredients
* Preserve batch history automatically
* Purchase date defaults to today's date

---

## Remove / Throw Out Food

Users can remove food from inventory without recalculating nutritional information manually.

Use cases:

* Throwing away spoiled food
* Correcting inventory mistakes

Users specify:

* Food name
* Amount to remove

### FIFO Consumption

Inventory deductions follow **First-In-First-Out (FIFO)** logic.

Older batches are consumed before newer batches.

Example:

Initial inventory:

```text
500 g Beef (June 1)
400 g Beef (June 6)
```

Remove:

```text
600 g Beef
```

Remaining:

```text
300 g Beef (June 6)
```

---

## Fridge Summary Dashboard

Displays overall nutritional availability.

Current metrics:

* Total calories available
* Total protein available
* Number of unique food items

Example:

```text
Calories: 14,520 kcal

Protein: 1,280 g

Foods: 8
```

---

## Inventory Filtering and Sorting

### Sorting

Users can sort inventory by:

* A–Z
* Date Added

### Filtering

Users can filter foods by category:

* Protein
* Fibre
* Carbs
* Others

Filter chips use subtle colour themes:

| Category | Style                             |
| -------- | --------------------------------- |
| Protein  | Soft grey with muted red border   |
| Fibre    | Soft grey with sage green border  |
| Carbs    | Soft grey with warm yellow border |
| Others   | Soft grey with neutral border     |

### Search

Users can search inventory by food name.

---

## Freshness Indicators

Inventory items display freshness based on the oldest batch remaining.

Examples:

```text
Today

1 day old

5 days old

Unknown
```

This helps prioritize foods that should be consumed soon.

---

## Daily Nutrition Tracker

Users can track food intake on a day-by-day basis.

Features:

* Multiple meals per day
* Multiple ingredients per meal
* Automatic calorie calculations
* Automatic protein calculations
* Automatic inventory deduction
* Historical day navigation

---

## Meal Logging

Users can create meal cards throughout the day.

Each meal card supports:

* Custom meal names
* Multiple ingredients per meal
* Quantity consumed for each ingredient
* Running meal nutrition totals

Example:

```text
Lunch

Ground Beef     225 g
Greek Yogurt    120 g
Eggs            2 pieces

725 kcal
68 g protein
```

---

## Automatic Inventory Deduction

When a meal is saved:

* Meal records are stored in the database.
* Daily nutritional totals are updated.
* Consumed quantities are automatically deducted from fridge inventory using FIFO logic.

This ensures fridge inventory accurately reflects actual food consumption.

---

## Daily Summary Dashboard

Each day displays cumulative intake totals.

Current metrics:

```text
Calories:
1540 kcal

Protein:
132 g
```

---

## Date Navigation

Users can navigate between days using previous and next arrows.

Features:

* Review historical nutrition records
* View previous meal logs
* Track consistency over time

Example:

```text
<    2026-06-07    >
```

Future versions will support editing and deleting past meal logs.

---

## Mobile-First Interface

Current UI optimizations include:

* Phone-sized development viewport
* Compact inventory cards
* Compact meal cards
* Collapsible grocery forms
* Search, filter, and sort controls optimized for mobile use
* Color-coded nutritional indicators
* Minimal data-entry workflows

---

## Collapsible Sections

The following sections support collapsing:

Fridge:

* Add Grocery
* Remove Portion

This allows users to focus primarily on viewing inventory while keeping data entry accessible.

---

## Project Structure

```text
MealPrepApp/

├── main.py
├── database.py
├── mealprep.db

├── screens/
│   ├── __init__.py
│   ├── fridge_page.py
│   └── daily_tracker_page.py

├── ui/
│   ├── __init__.py
│   ├── fridge_ui.py
│   └── daily_tracker_ui.py
```

---

## File Responsibilities

### main.py

* Application entry point
* Initializes database
* Launches top-level navigation

### database.py

Handles:

* Database initialization
* Ingredient management
* Batch tracking
* Inventory updates
* FIFO inventory deductions
* Meal logging
* Daily nutrition calculations

### screens/fridge_page.py

Handles:

* Fridge business logic
* Validation
* Connecting fridge UI actions to database operations

### screens/daily_tracker_page.py

Handles:

* Meal tracking logic
* Daily nutrition summaries
* Date navigation
* Meal saving operations

### ui/fridge_ui.py

Handles:

* Fridge user interface layout
* Inventory cards
* Filtering and sorting controls
* Search functionality
* Add/remove forms
* Freshness indicators
* Summary dashboard

### ui/daily_tracker_ui.py

Handles:

* Daily tracker interface
* Meal cards
* Ingredient inputs
* Daily summaries
* Date navigation controls

---

## Planned Features

### Meal Editing

Users will be able to:

* Edit saved meals
* Delete meals
* Restore inventory after meal deletion

---

### Fibre Tracking

Daily tracking of:

* Calories
* Protein
* Fibre

Example:

```text
Calories:
1500 / 1700 kcal

Protein:
125 / 130 g

Fibre:
22 / 25 g
```

---

### Cost Tracking

Each grocery purchase will include pricing information.

Future calculations:

* Cost per gram
* Daily food expenditure
* Monthly food spending trends

---

### Sustainability Estimates

Estimate how long current inventory supports nutritional goals.

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

Future progress tracking:

```text
Date       Weight

2026-06-01 68.0 kg
2026-06-08 67.2 kg
```

Used to monitor:

* Fat loss progress
* Bulking progress
* Weight maintenance trends

---

### Nutrition Goal System

Users will be able to set:

* Daily calorie goals
* Daily protein goals
* Daily fibre goals

Progress indicators will visualize adherence to goals.

---

## Motivation

MealPrep was created to solve common problems encountered during meal prepping:

* Forgetting what food is available
* Buying duplicate groceries unnecessarily
* Losing track of calories and protein intake
* Allowing groceries to spoil unnoticed
* Difficulty maintaining accountability during dieting phases
* Understanding how long food supplies will last

The goal is to provide a simple but powerful tool that combines:

* Inventory management
* Nutrition tracking
* Grocery planning
* Budget awareness
* Fitness accountability

into one intuitive mobile application.
