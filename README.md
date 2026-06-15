# Hospital ERP - HRM Module

This module contains Human Resource Management (HRM) functionality for the Hospital ERP system.

## Shift Management

### Shift Type

A DocType that defines shift types with timings and rules.

**Fields:**
- **Shift Type**: Unique identifier for the shift
- **Start Time**: When the shift begins
- **End Time**: When the shift ends
- **Working Hours**: Calculated automatically based on start/end times
- **Break Start/End Time**: Break period within the shift
- **Break Duration**: Length of break in minutes
- **Grace Periods**: Late entry and early exit grace periods
- **Overtime Settings**: Whether overtime is allowed and the overtime rate
- **Night Shift**: Flag for night shifts
- **Weekly Off Days**: Days off for this shift type

**Permissions:**
- System Manager: Full access
- HR Manager: Read, write, create (no delete)

### Shift Assignment

A DocType that assigns shift types to employees on specific dates.

**Fields:**
- **Employee**: The employee assigned to the shift
- **Shift Type**: The type of shift to assign
- **Shift Date**: The date of the shift
- **Status**: Current status of the assignment
- **Clock In/Out Times**: When the employee clocked in/out
- **Total Hours Worked**: Calculated automatically
- **Overtime Hours**: Calculated based on shift type rules

**Permissions:**
- System Manager: Full access
- HR Manager: Read, write, create (no delete)
- Employee: Read, write, create (no delete)

## Python Controllers

Each DocType has a corresponding Python controller file:
- `hrm/shift_type.py`: Handles Shift Type business logic
- `hrm/shift_assignment.py`: Handles Shift Assignment business logic

## Features

1. **Shift Timing Validation**: Ensures end time is after start time
2. **Break Validation**: Validates break start/end times
3. **Working Hours Calculation**: Automatically calculates working hours
4. **Overtime Calculation**: Calculates overtime based on shift type rules
5. **Shift Assignment Validation**: Prevents duplicate assignments
6. **Clock In/Out Tracking**: Tracks employee clock in/out times
7. **Role-Based Access Control**: Different permissions for different roles

## Usage

1. Create Shift Types to define different work schedules
2. Assign Shift Types to employees for specific dates
3. Track clock in/out times
4. Automatically calculate working hours and overtime

## Files Created

- `hospitalerpmodule/hrm/shift_type.json`: Shift Type DocType definition
- `hospitalerpmodule/hrm/shift_assignment.json`: Shift Assignment DocType definition
- `hospitalerpmodule/hrm/shift_type.py`: Shift Type Python controller
- `hospitalerpmodule/hrm/shift_assignment.py`: Shift Assignment Python controller
- `hospitalerpmodule/hrm/__init__.py`: Python package initialization
- `setup.py`: Python package setup configuration