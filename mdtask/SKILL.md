---
name: mdtask
description: A CLI tool for managing markdown task lists. Use when working with markdown-based task management, including creating, editing, filtering, and tracking tasks in markdown files. Triggers on requests like "manage tasks", "add task", "task list", "mark task done", or working with tasks.md files.
---

# mdtask

A CLI tool for managing markdown task lists.

## Installation

```bash
pip install mdtask
```

## Usage

All commands operate on `tasks.md` by default. Use `--file` to specify a different file.

### List tasks

```bash
task list
task list --file work.md
```

### Add a task

```bash
task add "Fix payment bug #backend +urgent due:2026-03-20"
```

A unique 6-character `id:` is automatically appended to each task.

### Mark a task as done

```bash
task done 015aec
```

### Edit a task

```bash
task edit 015aec "Updated task description #backend due:2026-04-01"
```

Preserves the checkbox state and `id:`.

### Remove a task

```bash
task remove 015aec
```

### Filter by tag

```bash
task tag "#backend"
task tag "+urgent"
```

### Filter by due date

```bash
task due 2026-03-20
```

### Show tasks due today

```bash
task today
```

### Show tasks due tomorrow

```bash
task tomorrow
```

### Show tasks due within the next 7 days

```bash
task week
```

## Task format

Tasks follow standard markdown checkbox syntax:

```
- [ ] Task description #tag +priority due:YYYY-MM-DD id:abc123
- [x] Completed task id:def456
```

| Field | Example | Description |
|---|---|---|
| `#tag` | `#backend` | Categorize tasks |
| `+priority` | `+urgent` | Mark priority |
| `due:` | `due:2026-03-20` | Set due date |
| `id:` | `id:015aec` | Auto-generated unique ID |
