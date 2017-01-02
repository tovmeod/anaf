"""
Project Management

The PM module allows to manage projects, their milestones and tasks.
Tasks may be assigned to one or more users registered within the system.

Each Task and Milestone is assigned a Status, one of TaskStatus instances,
which may be dynamically defined. Those Tasks and Milestones which are assigned
a Status with .hidden field set to True won't be displayed, unless the Status
is selected in Filters or an appropriate view.

The module defines Project, Milestone, Task, TaskStatus and TaskTimeSlot, in this order.
In this module I try to organize things in this order,
meaning tests for Project comes first, then the tests for Task and so on.
Also the order of the views inside the viewset is also respected.
"""
