<img src="https://github.com/user-attachments/assets/f0aa1054-51c1-41b3-b5ea-0111b1c67aef" alt="Deranged Frappe Barista" width="300">

### Jailbreak

Add destructive superpowers to any Frappe site.

## Features

Jailbreak provides several powerful capabilities that you probably don't want enabled on your Frappe sites... but if you do, they can be individually enabled/disabled:

### 🔀 Global Bulk Merge
- **Description**: Merge multiple records across any DocType
- **Location**: Available as "Merge Selected" action in all list views
- **Usage**: Select 2+ records in any list view and use the "Merge Selected" action

### 📦 Item Convert to Variant
- **Description**: Convert existing Items into variants of template Items
- **Location**: Item form → Actions → "Convert to Variant"
- **Usage**: Select a template item and specify attribute values to convert the current item

### 🔄 Version Restore
- **Description**: Restore documents from their version history
- **Location**: Version list view and individual Version forms
- **Usage**: 
  - **List View**: Select versions and use "Restore" bulk action
  - **Form View**: Click "Restore" button on individual versions

### 🖥️ Full Width Interface
- **Description**: Automatically enables full-width container layout
- **Usage**: Automatically applied when the app is installed (no capability gate)

## Configuration

All capabilities (except full-width) must be explicitly enabled in **Jailbreak Settings** before they become available to users.

Navigate to: **Setup → Jailbreak Settings**

Toggle the capabilities you want to enable.

## Safety Features

- **Capability Gating**: All destructive operations require explicit enablement
- **Permission Checks**: Backend validation ensures capabilities are enabled before execution
- **Error Handling**: Clear error messages when capabilities are disabled
- **Audit Trail**: All operations create proper audit trails and comments

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
bench get-app https://github.com/Avunu/jailbreak.git
bench install-app jailbreak
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/jailbreak
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
