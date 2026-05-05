# Appian SAIL Code Generator

Generate valid Appian SAIL interface code following the Aurora Design System and the SAIL Coding Guide standards defined in this project.

## Instructions

When invoked, generate complete, production-ready SAIL code for the requested interface type. Always follow every rule below — no exceptions.

---

## Core Rules

### 1. Always wrap everything in `a!localVariables()`
Every interface must start with `a!localVariables()`. Any function or component that references a local variable must be inside this top-level component.

```sail
a!localVariables(
  local!myVar: null,
  a!formLayout(...)
)
```

### 2. Top-level layouts
Use the appropriate top-level layout:
- Forms → `a!formLayout()`
- Dashboards → `a!headerContentLayout()`
- Panels → `a!panelLayout()`

### 3. Component syntax
All components follow `a!componentName(parameter: value)` — never omit the `a!` prefix.

### 4. Always include `contents` for container components
Section layouts, column layouts, card layouts all require a `contents` parameter.

---

## Local Variable Rules

- All local variables start with `local!`
- Variables with no initial value are type Null — cast them before comparisons
- Use `a!isNotNullOrEmpty()` / `a!isNullOrEmpty()` for null checks
- Use `a!defaultValue(local!var, fallback)` for defaults

```sail
a!localVariables(
  local!isActive: true,
  local!activeEmployees: a!queryEntity(
    entity: cons!EMPLOYEE_EE,
    query: a!query(
      filter: a!queryFilter("active", "=", local!isActive),
      pagingInfo: a!pagingInfo(1, 10)
    )
  ).data,
  ...
)
```

---

## Layout Components

### Section Layout
```sail
a!sectionLayout(
  label: "Section Title",
  labelHeadingTag: "H2",
  isCollapsible: true,
  marginBelow: "STANDARD",
  contents: {
    /* components here */
  }
)
```

### Columns Layout (responsive)
```sail
a!columnsLayout(
  columns: {
    a!columnLayout(
      width: "MEDIUM",
      contents: { /* left content */ }
    ),
    a!columnLayout(
      contents: { /* right content */ }
    )
  },
  stackWhen: {"PHONE", "TABLET_PORTRAIT"}
)
```
- Always include `stackWhen: {"PHONE", "TABLET_PORTRAIT"}` for responsive behavior
- Never use fixed widths on all columns — at least one must be AUTO for fluid layout
- Use empty `a!columnLayout()` components on either side to center content

### Card Layout
```sail
a!cardLayout(
  contents: { /* card content */ },
  style: "STANDARD",
  padding: "STANDARD",
  showBorder: true,
  shape: "SEMI_ROUNDED"
)
```

### Card Group Layout
```sail
a!cardGroupLayout(
  labelPosition: "COLLAPSED",
  cards: {
    a!cardLayout(contents: { /* Card 1 */ }),
    a!cardLayout(contents: { /* Card 2 */ })
  },
  spacing: "STANDARD",
  cardWidth: "MEDIUM",
  cardHeight: "AUTO"
)
```

---

## Input Components

### Text Field
```sail
a!textField(
  label: "Email Address",
  labelPosition: "ABOVE",
  value: local!email,
  saveInto: local!email,
  required: true,
  requiredMessage: "Email is required.",
  placeholder: "name@company.com"
)
```

### Paragraph Field
```sail
a!paragraphField(
  label: "Description",
  labelPosition: "ABOVE",
  value: local!description,
  saveInto: local!description,
  height: "MEDIUM",
  required: true
)
```

### Dropdown
```sail
a!dropdownField(
  label: "Department",
  labelPosition: "ABOVE",
  choiceLabels: {"Sales", "Marketing", "Engineering", "Support"},
  choiceValues: {"sales", "marketing", "eng", "support"},
  value: local!department,
  saveInto: local!department,
  placeholder: "Select a department",
  required: true
)
```

### Radio Buttons
```sail
a!radioButtonField(
  label: "Priority Level",
  labelPosition: "ABOVE",
  choiceLabels: {"High", "Medium", "Low"},
  choiceValues: {1, 2, 3},
  value: local!priority,
  saveInto: local!priority,
  choiceLayout: "STACKED"
)
```

### Date Field
```sail
a!dateField(
  label: "Target Date",
  labelPosition: "ABOVE",
  value: local!targetDate,
  saveInto: local!targetDate,
  instructions: "Leave blank if flexible."
)
```

### File Upload
```sail
a!fileUploadField(
  label: "Attachments",
  labelPosition: "ABOVE",
  value: local!attachments,
  saveInto: local!attachments,
  maxFiles: 5
)
```

### Checkbox
```sail
a!checkboxField(
  label: "Terms",
  labelPosition: "COLLAPSED",
  choiceLabels: {"I agree to the terms and conditions."},
  choiceValues: {true},
  value: if(local!agreed, {true}, {}),
  saveInto: {
    a!save(local!agreed, not(a!isNullOrEmpty(save!value)))
  },
  required: true
)
```

---

## Display Components

### Rich Text (use instead of a!linkField for links)
```sail
a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: {
    a!richTextItem(text: "Status: ", style: "STRONG"),
    a!richTextItem(text: "Active", color: "STANDARD")
  }
)
```
- Use `linkStyle: "STANDALONE"` unless the link is inline within a sentence
- Use `linkStyle: "INLINE"` only when linking within mixed text

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

### Buttons (always inside a!buttonArrayLayout or a!buttonLayout)
```sail
a!buttonArrayLayout(
  buttons: {
    a!buttonWidget(
      label: "Save Changes",
      style: "SOLID",
      color: "ACCENT",
      size: "STANDARD",
      loadingIndicator: true,
      saveInto: {
        /* Save actions here */
      }
    )
  },
  align: "END"
)
```

### Form Buttons (via a!buttonLayout on a!formLayout)
```sail
buttons: a!buttonLayout(
  primaryButtons: {
    a!buttonWidget(label: "Submit", submit: true, style: "SOLID")
  },
  secondaryButtons: {
    a!buttonWidget(label: "Cancel", value: true, style: "OUTLINE", saveInto: local!showCancelDialog)
  }
)
```

---

## Validation Patterns

```sail
validations: {
  if(
    and(
      a!isNotNullOrEmpty(local!value),
      len(local!value) < 3
    ),
    "Must be at least 3 characters.",
    null
  )
}
```

For date validation:
```sail
validations: {
  if(
    and(a!isNotNullOrEmpty(local!date), local!date < today()),
    "Date cannot be in the past.",
    null
  )
}
```

---

## Logical Operators

SAIL uses function-style logical operators — never symbolic ones:

```sail
/* Correct */
and(condition1, condition2)
or(condition1, condition2)
not(condition)

/* WRONG — causes errors */
condition1 && condition2
condition1 || condition2
```

---

## Visibility Control

```sail
showWhen: a!isNotNullOrEmpty(local!selectedCustomer)
showWhen: a!isNullOrEmpty(local!basicInfo)
```

---

## Accessibility

- Use `labelHeadingTag: "H2"` on `a!sectionLayout` labels
- Use `a!headingField` with `headingTag` for explicit heading hierarchy (H1 → H2 → H3)
- Always set `labelPosition` explicitly: `"ABOVE"`, `"ADJACENT"`, `"COLLAPSED"`, or `"JUSTIFIED"`
- Include `instructions` for fields needing extra context
- Include `accessibilityText` for image fields

---

## Test Data Guidelines

- Use generic professional names: "Sarah Johnson", "Michael Chen"
- Use realistic business data, not sequential values (1, 2, 3)
- Use relative dates: `today()`, `today() + 30`, `today() - 15`
- Use common statuses: "Pending", "Processing", "Shipped", "Delivered", "Cancelled"
- Use common departments: "Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"
- Use realistic amounts: 1250.00, 875.50, 2198.75 (not 999,999,999)

---

## Common Errors to Avoid

| Wrong | Right |
|---|---|
| `a!richTextItem(text: text(local!val, "format"))` | `a!richTextItem(text: local!val)` — only use `text()` to convert non-strings |
| `a!gridField(showSearchBox: true)` without `data` Record Type | Always pair `showSearchBox` with a Record Type `data` source |
| Symbolic operators `&&`, `\|\|` | Use `and()`, `or()`, `not()` |
| Missing `contents` parameter | Always include `contents: {}` on container components |

---

## Interface Template — Basic Form

```sail
a!localVariables(
  local!firstName: null,
  local!lastName: null,

  a!formLayout(
    titleBar: a!headerTemplateSimple(title: "Form Title"),
    contents: {
      a!sectionLayout(
        label: "Section Label",
        labelHeadingTag: "H2",
        isCollapsible: true,
        marginBelow: "STANDARD",
        contents: {
          a!columnsLayout(
            columns: {
              a!columnLayout(
                contents: {
                  a!textField(
                    label: "First Name",
                    labelPosition: "ABOVE",
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
                    labelPosition: "ABOVE",
                    value: local!lastName,
                    saveInto: local!lastName,
                    required: true
                  )
                }
              )
            },
            stackWhen: {"PHONE", "TABLET_PORTRAIT"}
          )
        }
      )
    },
    buttons: a!buttonLayout(
      primaryButtons: {
        a!buttonWidget(label: "Submit", submit: true, style: "SOLID")
      },
      secondaryButtons: {
        a!buttonWidget(label: "Cancel", value: true, style: "OUTLINE", saveInto: local!showCancelDialog)
      }
    )
  )
)
```

---

## What to Generate

When the user runs `/appian <description>`, generate complete SAIL code for the described interface using all the rules above. Include:
1. All required local variables
2. Proper form/layout structure
3. All input fields with validation
4. Responsive column layouts with `stackWhen`
5. Submit and Cancel buttons in `a!buttonLayout`
6. Null/error state handling with `a!messageBanner`
7. Realistic test data values in comments where helpful

$ARGUMENTS
