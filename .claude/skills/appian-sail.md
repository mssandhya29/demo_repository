# Appian SAIL Development Skill

## Purpose

Generate valid Appian SAIL interfaces following documented component patterns and best practices. Every development result produced by this skill **must always be packaged as an Appian-importable ZIP file**.

---

## Output Requirement: Appian Importable ZIP

After generating any SAIL interface code, you MUST produce a ZIP package that Appian can import. Use the Python script below every time to create the package.

### Appian Package Structure

```
<PackageName>.zip
├── _manifest.json
└── interface/
    └── <InterfaceName>.json
```

### ZIP Generation Script

Save this as `package_appian.py` and run it, or inline the logic directly:

```python
import json
import zipfile
import os

def create_appian_package(interface_name: str, sail_code: str, output_path: str = None):
    """
    Creates an Appian-importable ZIP package for a SAIL interface.

    Args:
        interface_name: The name of the Appian interface object (no spaces).
        sail_code: The full SAIL expression string.
        output_path: File path for the output ZIP. Defaults to <interface_name>.zip
    """
    if output_path is None:
        output_path = f"{interface_name}.zip"

    manifest = {
        "appianPackageExportFormatVersion": "1",
        "objects": [
            {
                "type": "Interface",
                "name": interface_name
            }
        ]
    }

    interface_obj = {
        "entity": {
            "type": "Interface",
            "name": interface_name
        },
        "sailCode": sail_code
    }

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("_manifest.json", json.dumps(manifest, indent=2))
        zf.writestr(
            f"interface/{interface_name}.json",
            json.dumps(interface_obj, indent=2)
        )

    print(f"Package created: {output_path}")
    return output_path


# Example usage — replace with actual interface name and SAIL code:
if __name__ == "__main__":
    sail_code = """
a!localVariables(
  /* local variables here */
  a!formLayout(
    contents: {
      /* interface contents */
    }
  )
)
""".strip()

    create_appian_package(
        interface_name="MyInterface",
        sail_code=sail_code,
        output_path="MyInterface.zip"
    )
```

### Workflow When Using This Skill

1. Gather requirements for the interface.
2. Write valid SAIL code following all rules in this document.
3. Run the packaging script to produce `<InterfaceName>.zip`.
4. Confirm the ZIP was created and share its path with the user.

---

## Core SAIL Principles

### 1. Interface Structure

- **Top-level layouts**: `a!formLayout()`, `a!headerContentLayout()`, `a!paneLayout()`
- **Nested layouts**: `a!sectionLayout()`, `a!columnsLayout()`, `a!cardLayout()`
- Always include the `contents` parameter for all container components.

### 2. Component Syntax

All SAIL components follow the pattern: `a!componentName(parameter: value)`

```sail
a!textField(
  label: "Customer Name",
  value: local!customerName,
  saveInto: local!customerName,
  required: true
)
```

---

## Local Variables

**IMPORTANT**: All interfaces MUST start with `a!localVariables()`. Any function or component that references local variables must be wrapped inside this top-level component.

### Local Variable Types

Local variables have no fixed type — the type is determined by the assigned value at any moment.

```sail
a!localVariables(
  local!isActive: true,
  local!activeEmployees: a!queryEntity(
    entity: cons!EMPLOYEE_DSE,
    query: a!query(
      filter: a!queryFilter("active", "=", local!isActive),
      pagingInfo: a!pagingInfo(1, 10)
    )
  ).data,
  local!activeEmployees
)
```

### Variables Without an Initial Value

Variables without an initial value are of type **Null**. Cast them to the expected type before comparisons:

```sail
a!localVariables(
  local!quantity,
  a!integerField(
    label: "Quantity",
    value: local!quantity,
    saveInto: local!quantity,
    validations: if(
      tointeger(local!quantity) < 0,
      "Quantity must be greater than 0",
      ""
    )
  )
)
```

### Updating a Variable Value

A variable's type changes when a new value is saved into it. For example, if `local!number` starts as Integer but a floating-point field saves into it, it becomes Decimal.

---

## Test Data Guidelines

Use realistic but generic test data.

### Naming Conventions

**Use generic, professional names:**

```sail
local!employees: {
  a!map(name: "Sarah Johnson", department: "Engineering", id: 1001),
  a!map(name: "Michael Chen", department: "Marketing", id: 1002),
  a!map(name: "Emily Rodriguez", department: "Sales", id: 1003)
}
```

Avoid: real public figures, culturally insensitive names, or controversial content.

### Data Values

Use realistic business data:

```sail
local!orders: {
  a!map(orderNumber: "ORD-2024-001", amount: 1250.00, status: "Shipped"),
  a!map(orderNumber: "ORD-2024-002", amount: 875.50, status: "Processing"),
  a!map(orderNumber: "ORD-2024-003", amount: 2100.75, status: "Delivered")
}
```

Use placeholder patterns for sensitive data (emails, phone numbers).

### Quantities and Amounts

Use varied, realistic numbers. Avoid sequential (1, 2, 3) or unrealistically round/large values.

```sail
local!salesData: {45000, 52000, 48000, 61000, 58000}
```

### Dates and Times

Use `today()` for relative dates:

```sail
local!projects: {
  a!map(name: "Website Redesign", startDate: today() - 45, dueDate: today() + 30),
  a!map(name: "Mobile App", startDate: today() - 30, dueDate: today() + 75)
}
```

### Status and Category Values

```sail
/* Order statuses */
"Pending", "Processing", "Shipped", "Delivered", "Cancelled"

/* Project statuses */
"Planning", "In Progress", "Review", "Complete", "On Hold"

/* Priority levels */
"Low", "Medium", "High", "Critical"

/* Departments */
"Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"
```

### Comments in Examples

Use helpful placeholder comments:

```sail
a!startProcess(
  processModel: cons!PM_EMPLOYEE_ONBOARDING,
  processParameters: {
    employee: local!employeeData,
    department: local!selectedDepartment
  },
  onSuccess: {
    /* Add success handling logic here */
    a!save(local!showConfirmation, true)
  },
  onError: {
    /* Add error handling logic here */
    a!save(local!errorMessage, "Failed to start onboarding process")
  }
)
```

---

## Essential Layout Components

### Section Layout

Groups related content with optional collapsible functionality:

```sail
a!sectionLayout(
  label: "Customer Information",
  labelHeadingTag: "H2",
  contents: {
    /* Components go here */
  },
  isCollapsible: true,
  marginBelow: "STANDARD"
)
```

### Columns Layout

Creates responsive multi-column layouts:

```sail
a!columnsLayout(
  columns: {
    a!columnLayout(
      width: "MEDIUM",
      contents: {
        /* Left column content */
      }
    ),
    a!columnLayout(
      width: "WIDE",
      contents: {
        /* Right column content */
      }
    )
  },
  stackWhen: {"PHONE", "TABLET_PORTRAIT"}
)
```

Use empty `a!columnLayout` components on either side of a column to center content.

### Card Layout

Provides visual grouping with styling options:

```sail
a!cardLayout(
  contents: {
    /* Card content */
  },
  style: "STANDARD",
  padding: "STANDARD",
  showBorder: true,
  shape: "SEMI_ROUNDED"
)
```

### Card Group Layout

Displays an arrangement of cards with equal width and height. Prefer this whenever multiple cards are displayed together:

```sail
a!cardGroupLayout(
  labelPosition: "COLLAPSED",
  cards: {
    a!cardLayout(contents: { /* Card content */ }),
    a!cardLayout(contents: { /* Card content */ }),
    a!cardLayout(contents: { /* Card content */ })
  },
  spacing: "STANDARD",
  cardWidth: "MEDIUM",
  cardHeight: "AUTO"
)
```

---

## Common Input Components

### Text Field

```sail
a!textField(
  label: "Email Address",
  labelPosition: "ABOVE",
  value: local!email,
  saveInto: local!email,
  required: true
)
```

### Dropdown

```sail
a!dropdownField(
  label: "Department",
  choiceLabels: {"Sales", "Marketing", "Engineering", "Support"},
  choiceValues: {"sales", "marketing", "eng", "support"},
  value: local!department,
  saveInto: local!department,
  placeholder: "Select a department"
)
```

### Radio Buttons

```sail
a!radioButtonField(
  label: "Priority Level",
  choiceLabels: {"High", "Medium", "Low"},
  choiceValues: {1, 2, 3},
  value: local!priority,
  saveInto: local!priority,
  choiceLayout: "STACKED"
)
```

---

## Display Components

### Rich Text Display

```sail
a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: {
    a!richTextItem(text: "Status: ", style: "STRONG"),
    a!richTextItem(
      text: "Active",
      color: "STANDARD"
    )
  }
)
```

### Tag Field

```sail
a!tagField(
  labelPosition: "COLLAPSED",
  tags: {
    a!tagItem(text: "Urgent", backgroundColor: "NEGATIVE"),
    a!tagItem(text: "Customer Facing", backgroundColor: "ACCENT")
  }
)
```

---

## Action Components

### Button

**IMPORTANT**: Button widgets should generally be placed inside `a!buttonArrayLayout`. Exceptions:
- `a!formLayout` uses `a!buttonLayout` for the `buttons` parameter.
- `a!wizardLayout` takes `a!buttonWidget` directly in `primaryButtons` and `secondaryButtons`.

```sail
a!buttonArrayLayout(
  buttons: {
    a!buttonWidget(
      label: "Save Changes",
      style: "SOLID",
      color: "ACCENT",
      size: "STANDARD",
      value: true,
      loadingIndicator: true,
      saveInto: {
        /* Save actions here */
        /*a!save(local!submitted, save!value) */
      }
    )
  },
  align: "END"
)
```

### Link

Use `a!richTextItem` instead of `a!linkField` for links:

```sail
a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: {
    a!richTextItem(
      text: "Visit site",
      link: a!safeLink(uri: "http://www.appian.com"),
      linkStyle: "STANDALONE"
    )
  }
)
```

**Link Style Rule**: Use `INLINE` for `linkStyle` ONLY when linked text is part of a sentence with other unlinked text. Otherwise use `STANDALONE`.

---

## Data Display Components

### Read-Only Grid

```sail
a!gridField(
  label: "Recent Orders",
  data: local!orders,
  columns: {
    a!gridColumn(
      label: "Order ID",
      sortField: "orderId",
      value: fv!row.orderId
    ),
    a!gridColumn(
      label: "Customer",
      sortField: "customerName",
      value: a!linkField(
        links: {
          a!recordLink(
            label: fv!row.customerName,
            recordType: recordType!Customer,
            identifier: fv!row.customerId
          )
        }
      )
    ),
    a!gridColumn(
      label: "Status",
      value: a!tagField(
        tags: a!tagItem(
          text: fv!row.status,
          backgroundColor: if(
            fv!row.status = "Complete",
            "POSITIVE",
            "SECONDARY"
          )
        )
      )
    )
  },
  showSearchBox: true,
  showRefreshButton: true
)
```

---

## Chart Components

### Column Chart

```sail
a!columnChartField(
  label: "Sales by Quarter",
  categories: {"Q1", "Q2", "Q3", "Q4"},
  series: {
    a!chartSeries(
      label: "2024",
      data: {45000, 52000, 48000, 61000}
    )
  },
  colorScheme: "RAINFOREST",
  showLegend: true,
  height: "MEDIUM"
)
```

---

## Accessibility Best Practices

### Heading Hierarchy

```sail
a!headingField(
  text: "Customer Dashboard",
  size: "LARGE",
  headingTag: "H1"
),
a!sectionLayout(
  label: "Account Information",
  labelHeadingTag: "H2",
  contents: {
    a!headingField(
      text: "Contact Details",
      size: "MEDIUM",
      headingTag: "H3"
    )
  }
)
```

### Form Labels and Instructions

```sail
a!textField(
  label: "Social Security Number",
  instructions: "Enter your 9-digit SSN without dashes",
  value: local!ssn,
  saveInto: local!ssn,
  validationGroup: "personal_info",
  accessibilityText: "Social Security Number for tax purposes"
)
```

---

## Common Parameter Patterns

### Visibility Control

```sail
showWhen: a!isNotNullOrEmpty(local!selectedCustomer)
```

### Validation Patterns

```sail
validations: {
  if(len(local!value) < 3, "Must be at least 3 characters", null),
  if(a!isNullOrEmpty(local!value), "This field is required", null)
}
```

### Margin Control

```sail
marginAbove: "STANDARD",
marginBelow: "MORE"
```

### Label Positioning

```sail
labelPosition: "ABOVE"  /* ABOVE, ADJACENT, COLLAPSED, JUSTIFIED */
```

---

## Responsive Design

### Centering Single-Column Content

For single-column content, use a three-column layout with hidden margin columns:

```sail
a!columnsLayout(
  columns: {
    a!columnLayout(
      width: "AUTO",
      showWhen: a!isPageWidth({"DESKTOP","DESKTOP_WIDE"})
    ), /* left margin — hidden on smaller screens */
    a!columnLayout(
      width: if(a!isPageWidth({"DESKTOP","DESKTOP_WIDE"}), "WIDE_PLUS", "AUTO"),
      contents: {
        /* All page content goes here */
      }
    ), /* main content — fixed width on desktop, AUTO on mobile/tablet */
    a!columnLayout(
      width: "AUTO",
      showWhen: a!isPageWidth({"DESKTOP","DESKTOP_WIDE"})
    ) /* right margin — hidden on smaller screens */
  }
)
```

**Key Principles**:
- Always include `AUTO` columns: at least one column must have `width: "AUTO"` for fluid layout.
- Hide margin columns: use `showWhen: a!isPageWidth({"DESKTOP","DESKTOP_WIDE"})` to hide margins on mobile/tablet.
- Never use all fixed widths — this causes responsive issues.

### Side by Side Layout

```sail
a!sideBySideLayout(
  items: {
    a!sideBySideItem(
      width: "MINIMIZE",
      item: a!imageField(
        labelPosition: "COLLAPSED",
        images: a!userImage(user: local!userId),
        size: "SMALL"
      )
    ),
    a!sideBySideItem(
      item: a!richTextDisplayField(
        labelPosition: "COLLAPSED",
        value: local!userName
      )
    )
  },
  alignVertical: "MIDDLE",
  stackWhen: {"PHONE"}
)
```

---

## Interface Templates

### Basic Form

```sail
a!formLayout(
  titleBar: a!headerTemplateSimple(title: "New Customer Registration"),
  contents: {
    a!sectionLayout(
      label: "Basic Information",
      contents: {
        a!columnsLayout(
          columns: {
            a!columnLayout(
              contents: {
                a!textField(
                  label: "First Name",
                  value: local!firstName,
                  saveInto: local!firstName,
                  required: true
                )
              }
            ),
            a!columnLayout(
              contents: {
                a!textField(
                  label: "Last Name",
                  value: local!lastName,
                  saveInto: local!lastName,
                  required: true
                )
              }
            )
          }
        )
      }
    )
  },
  buttons: a!buttonLayout(
    primaryButtons: {
      a!buttonWidget(
        label: "Submit",
        submit: true,
        style: "SOLID"
      )
    },
    secondaryButtons: {
      a!buttonWidget(
        label: "Cancel",
        value: true,
        style: "OUTLINE",
        saveInto: local!showCancelDialog
      )
    }
  )
)
```

### Dashboard Layout

```sail
a!headerContentLayout(
  header: {
    a!cardLayout(
      contents: {
        a!richTextDisplayField(
          labelPosition: "COLLAPSED",
          value: {
            a!richTextItem(
              text: "Sales Dashboard",
              size: "LARGE",
              style: "STRONG"
            )
          }
        )
      },
      style: "ACCENT"
    )
  },
  contents: {
    a!columnsLayout(
      columns: {
        a!columnLayout(
          width: "NARROW",
          contents: {
            /* Sidebar content */
          }
        ),
        a!columnLayout(
          contents: {
            /* Main content area */
          }
        )
      }
    )
  }
)
```

---

## Logical Operators

SAIL uses **function-style** logical operators — never symbolic operators:

```sail
/* Correct */
and(condition1, condition2, condition3)
or(condition1, condition2, condition3)
not(condition)

/* WRONG — causes errors */
condition1 and condition2
condition1 or condition2
```

Examples:

```sail
/* Multiple conditions in showWhen */
showWhen: and(
  a!isNotNullOrEmpty(local!selectedItem),
  local!isEditable,
  local!hasPermission
)

/* Complex condition in if statement */
if(
  or(
    a!isNullOrEmpty(local!value),
    not(typename(typeof(local!value)) = "Number (Integer)"),
    tointeger(local!value) < 0
  ),
  "Please enter a valid positive number",
  null
)
```

These functions accept any number of arguments:

```sail
and(condition1, condition2, condition3, condition4)
or(option1, option2, option3, option4, option5)
```

---

## Null Checking and Default Values

### Null Checking Functions

```sail
/* Check that a variable is NOT null or empty */
a!localVariables(
  local!basicInfo: "some content",
  a!sectionLayout(
    label: "Additional Info",
    contents: {},
    showWhen: a!isNotNullOrEmpty(local!basicInfo)
  )
)

/* Check that a variable IS null or empty */
a!localVariables(
  local!basicInfo: null,
  a!messageBanner(
    icon: "info-circle",
    primaryText: "Enter the basic info to get started",
    showWhen: a!isNullOrEmpty(local!basicInfo)
  )
)
```

### Default Values

```sail
a!localVariables(
  local!cookiePreference: null,
  a!textField(
    label: "Cookie Preference",
    value: a!defaultValue(local!cookiePreference, "Reject All"),
    readOnly: true
  )
)
```

---

## Common Errors and How to Avoid Them

### 1. Overuse of `text()` Function

Use `text()` **only** for converting non-text values to strings, not for string literals.

```sail
/* WRONG */
a!richTextItem(text: text("Status: Active"), style: "STRONG")

/* CORRECT */
a!richTextItem(text: "Status: Active", style: "STRONG")

/* CORRECT — converting a number */
a!richTextItem(text: text(local!numericValue, `format`), style: "STRONG")
```

### 2. Grid Component Validation Errors

`showSearchBox` only works with Record Type data sources:

```sail
/* WRONG — array data with showSearchBox */
a!gridField(data: local!arrayData, showSearchBox: true, columns: { /* ... */ })

/* CORRECT — Record Type data */
a!gridField(data: a!recordData(recordType!Employee), showSearchBox: true, columns: { /* ... */ })

/* CORRECT — array data without showSearchBox */
a!gridField(data: local!arrayData, columns: { /* ... */ })
```

### 3. Layout Width Validation Errors

**Side by Side Layout** valid widths: `AUTO`, `MINIMIZE`, `1X`–`10X`

```sail
/* WRONG */
a!sideBySideItem(width: "WIDE", item: /* component */)

/* CORRECT */
a!sideBySideItem(width: "AUTO", item: /* component */)
a!sideBySideItem(width: "3X", item: /* component */)
```

**Form/Wizard Layout** valid `contentsWidth`: `FULL`, `WIDE`, `MEDIUM`, `NARROW`, `EXTRA_NARROW`

```sail
/* WRONG */
a!formLayout(contentsWidth: "NARROW_PLUS", contents: { /* ... */ })

/* CORRECT */
a!formLayout(contentsWidth: "MEDIUM", contents: { /* ... */ })
```

### 4. Component Confusion Errors

Use `a!milestoneField` with `steps`, not the non-existent `a!milestoneStep`:

```sail
/* WRONG */
a!milestoneStep(label: "Step 1", status: "COMPLETE")

/* CORRECT */
a!milestoneField(
  steps: {
    "Submit Customer Request",
    "Set Up On-Site Appt",
    "File Assessment",
    "Submit Proposal",
    "Finalize Repairs"
  }
)
```

### 5. Invalid Parameter Values

**Button colors**: Valid values are `ACCENT`, `NEGATIVE`, `SECONDARY`, or any hex value.

```sail
/* WRONG */
a!buttonWidget(label: "Submit", color: "POSITIVE", style: "SOLID")

/* CORRECT */
a!buttonWidget(label: "Submit", color: "ACCENT", style: "SOLID")
```

**Progress bar colors**: Valid values are `ACCENT`, `POSITIVE`, `NEGATIVE`, `WARN`, or any hex value.

```sail
/* WRONG */
a!progressBarField(percentage: 75, color: "SECONDARY")

/* CORRECT */
a!progressBarField(percentage: 75, color: "POSITIVE")
```

**Checkbox value/choice mismatch**: The `value` must be in `choiceValues`:

```sail
/* WRONG */
a!checkboxField(choiceLabels: {"Confirmed"}, choiceValues: {true}, value: false)

/* CORRECT */
a!checkboxField(choiceLabels: {"Confirmed"}, choiceValues: {true}, value: true)
```

### 6. Unavailable Components

Do not use `a!dateRangeField` — it does not exist:

```sail
/* WRONG */
a!dateRangeField(startValue: local!startDate, endValue: local!endDate)

/* CORRECT — use separate date fields */
a!columnsLayout(
  columns: {
    a!columnLayout(contents: { a!dateField(label: "Start Date", value: local!startDate, saveInto: local!startDate) }),
    a!columnLayout(contents: { a!dateField(label: "End Date", value: local!endDate, saveInto: local!endDate) })
  }
)
```

### 7. Layout Restriction Errors

`a!columnsLayout` cannot be nested inside `a!sideBySideItem`:

```sail
/* WRONG */
a!sideBySideItem(item: a!columnsLayout(columns: { /* ... */ }))

/* CORRECT — wrap in columnsLayout first */
a!columnsLayout(
  columns: {
    a!columnLayout(
      contents: {
        a!sideBySideLayout(items: { a!sideBySideItem(item: /* single component */) })
      }
    )
  }
)
```

### 8. Redundant Elements Errors

Never add asterisks to required field labels — Appian adds them automatically:

```sail
/* WRONG */
a!textField(label: "First Name *", required: true)

/* CORRECT */
a!textField(label: "First Name", required: true)
```

### 9. Invalid Chart Parameters

For `a!pieChartField`, use `seriesLabelStyle: "LEGEND"` instead of `showLegend`:

```sail
/* WRONG */
a!pieChartField(series: { /* ... */ }, showLegend: true)

/* CORRECT */
a!pieChartField(series: { /* ... */ }, seriesLabelStyle: "LEGEND")
```

### 10. Button Style Inconsistency for `a!fileUploadField`

`a!fileUploadField` and `a!signatureField` use **old** button style names:

```sail
/* WRONG for fileUploadField */
a!fileUploadField(buttonStyle: "SOLID", saveInto: {}, validations: {})

/* CORRECT — use old style names: "PRIMARY", "SECONDARY", "STANDARD", "LINK" */
a!fileUploadField(buttonStyle: "STANDARD", saveInto: {}, validations: {})
```

### 11. Valid Icons

Only use icons from the supported set listed in `branding/icons`. Do not guess icon names:

```sail
/* WRONG */
a!richTextDisplayField(value: { a!richTextIcon(icon: "shield-alt") })

/* CORRECT */
a!richTextDisplayField(value: { a!richTextIcon(icon: "shield") })
```

---

## Error Prevention Checklist

Before finalizing any SAIL code, verify:

- [ ] **`text()` usage**: Only for type conversion, not string literals
- [ ] **Grid configuration**: `showSearchBox` only with Record Type data sources
- [ ] **Layout widths**:
  - `sideBySideLayout`: `AUTO`, `MINIMIZE`, `1X`–`10X`
  - `formLayout`/`wizardLayout`: `FULL`, `WIDE`, `MEDIUM`, `NARROW`, `EXTRA_NARROW`
- [ ] **Component names**: Use exact names from documentation
- [ ] **Parameter values**: Use only documented parameter values
- [ ] **Component parameters**: Include only documented parameters
- [ ] **Component availability**: Verify component exists in current Appian version
- [ ] **Layout nesting**: Check component compatibility within layouts
- [ ] **Required input indicators**: Do not add asterisks — added automatically
- [ ] **Pie chart legend syntax**: Use `seriesLabelStyle: "LEGEND"`
- [ ] **`a!fileUploadField` button styles**: Use old style values (`PRIMARY`, `SECONDARY`, `STANDARD`, `LINK`)
- [ ] **Valid icons**: Confirm icon is in supported set before including
- [ ] **ZIP package created**: Output has been packaged as an Appian-importable ZIP
