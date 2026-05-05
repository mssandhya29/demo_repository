a!localVariables(
  /* Requester Info */
  local!firstName: null,
  local!lastName: null,
  local!email: null,
  local!phone: null,

  /* Request Details */
  local!requestTitle: null,
  local!department: null,
  local!priority: null,
  local!requestType: null,
  local!description: null,
  local!targetDate: null,

  /* Additional Info */
  local!attachments: null,
  local!acknowledgement: false,

  /* Form State */
  local!submitted: false,
  local!showCancelDialog: false,
  local!errorMessage: null,
  local!validationErrors: {},

  a!formLayout(
    titleBar: a!headerTemplateSimple(title: "New Request Intake Form"),
    contents: {

      /* ── Section 1: Requester Information ── */
      a!sectionLayout(
        label: "Requester Information",
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
                    required: true,
                    requiredMessage: "First name is required.",
                    validations: {
                      if(
                        and(
                          a!isNotNullOrEmpty(local!firstName),
                          len(local!firstName) < 2
                        ),
                        "First name must be at least 2 characters.",
                        null
                      )
                    }
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
                    required: true,
                    requiredMessage: "Last name is required.",
                    validations: {
                      if(
                        and(
                          a!isNotNullOrEmpty(local!lastName),
                          len(local!lastName) < 2
                        ),
                        "Last name must be at least 2 characters.",
                        null
                      )
                    }
                  )
                }
              )
            },
            stackWhen: {"PHONE", "TABLET_PORTRAIT"}
          ),
          a!columnsLayout(
            columns: {
              a!columnLayout(
                contents: {
                  a!textField(
                    label: "Email Address",
                    labelPosition: "ABOVE",
                    value: local!email,
                    saveInto: local!email,
                    required: true,
                    requiredMessage: "Email address is required.",
                    placeholder: "name@company.com",
                    validations: {
                      if(
                        and(
                          a!isNotNullOrEmpty(local!email),
                          not(contains(local!email, "@"))
                        ),
                        "Please enter a valid email address.",
                        null
                      )
                    }
                  )
                }
              ),
              a!columnLayout(
                contents: {
                  a!textField(
                    label: "Phone Number",
                    labelPosition: "ABOVE",
                    value: local!phone,
                    saveInto: local!phone,
                    placeholder: "(555) 123-4567",
                    instructions: "Optional. Include country code for international numbers."
                  )
                }
              )
            },
            stackWhen: {"PHONE", "TABLET_PORTRAIT"}
          )
        }
      ),

      /* ── Section 2: Request Details ── */
      a!sectionLayout(
        label: "Request Details",
        labelHeadingTag: "H2",
        isCollapsible: true,
        marginBelow: "STANDARD",
        contents: {
          a!textField(
            label: "Request Title",
            labelPosition: "ABOVE",
            value: local!requestTitle,
            saveInto: local!requestTitle,
            required: true,
            requiredMessage: "A request title is required.",
            placeholder: "Brief summary of your request",
            validations: {
              if(
                and(
                  a!isNotNullOrEmpty(local!requestTitle),
                  len(local!requestTitle) < 5
                ),
                "Title must be at least 5 characters.",
                null
              )
            }
          ),
          a!columnsLayout(
            columns: {
              a!columnLayout(
                contents: {
                  a!dropdownField(
                    label: "Department",
                    labelPosition: "ABOVE",
                    choiceLabels: {
                      "Engineering",
                      "Marketing",
                      "Sales",
                      "HR",
                      "Finance",
                      "Operations"
                    },
                    choiceValues: {
                      "engineering",
                      "marketing",
                      "sales",
                      "hr",
                      "finance",
                      "operations"
                    },
                    value: local!department,
                    saveInto: local!department,
                    placeholder: "Select a department",
                    required: true,
                    requiredMessage: "Please select a department."
                  )
                }
              ),
              a!columnLayout(
                contents: {
                  a!dropdownField(
                    label: "Request Type",
                    labelPosition: "ABOVE",
                    choiceLabels: {
                      "New Feature",
                      "Bug Fix",
                      "Access Request",
                      "Data Change",
                      "Process Improvement",
                      "Other"
                    },
                    choiceValues: {
                      "feature",
                      "bug",
                      "access",
                      "data",
                      "process",
                      "other"
                    },
                    value: local!requestType,
                    saveInto: local!requestType,
                    placeholder: "Select a request type",
                    required: true,
                    requiredMessage: "Please select a request type."
                  )
                }
              )
            },
            stackWhen: {"PHONE", "TABLET_PORTRAIT"}
          ),
          a!radioButtonField(
            label: "Priority Level",
            labelPosition: "ABOVE",
            choiceLabels: {"Critical", "High", "Medium", "Low"},
            choiceValues: {"critical", "high", "medium", "low"},
            value: local!priority,
            saveInto: local!priority,
            choiceLayout: "STACKED",
            required: true,
            requiredMessage: "Please select a priority level."
          ),
          a!dateField(
            label: "Requested Target Date",
            labelPosition: "ABOVE",
            value: local!targetDate,
            saveInto: local!targetDate,
            instructions: "When do you need this completed? Leave blank if flexible.",
            validations: {
              if(
                and(
                  a!isNotNullOrEmpty(local!targetDate),
                  local!targetDate < today()
                ),
                "Target date cannot be in the past.",
                null
              )
            }
          ),
          a!paragraphField(
            label: "Description",
            labelPosition: "ABOVE",
            value: local!description,
            saveInto: local!description,
            required: true,
            requiredMessage: "Please describe your request.",
            placeholder: "Provide details about your request, including context, expected outcome, and any constraints.",
            height: "MEDIUM",
            validations: {
              if(
                and(
                  a!isNotNullOrEmpty(local!description),
                  len(local!description) < 20
                ),
                "Description must be at least 20 characters.",
                null
              )
            }
          )
        }
      ),

      /* ── Section 3: Attachments ── */
      a!sectionLayout(
        label: "Supporting Documents",
        labelHeadingTag: "H2",
        isCollapsible: true,
        marginBelow: "STANDARD",
        contents: {
          a!fileUploadField(
            label: "Attachments",
            labelPosition: "ABOVE",
            value: local!attachments,
            saveInto: local!attachments,
            instructions: "Upload any relevant documents, screenshots, or supporting files.",
            maxFiles: 5
          )
        }
      ),

      /* ── Section 4: Acknowledgement ── */
      a!sectionLayout(
        label: "Acknowledgement",
        labelHeadingTag: "H2",
        isCollapsible: false,
        marginBelow: "STANDARD",
        contents: {
          a!checkboxField(
            label: "I confirm the information provided is accurate and complete.",
            labelPosition: "COLLAPSED",
            choiceLabels: {
              "I confirm the information provided is accurate and complete."
            },
            choiceValues: {true},
            value: if(local!acknowledgement, {true}, {}),
            saveInto: {
              a!save(
                local!acknowledgement,
                not(a!isNullOrEmpty(save!value))
              )
            },
            required: true,
            requiredMessage: "You must acknowledge before submitting."
          )
        }
      ),

      /* ── Error banner (shown only when submission fails) ── */
      a!messageBanner(
        icon: "warning",
        primaryText: local!errorMessage,
        showWhen: a!isNotNullOrEmpty(local!errorMessage)
      )

    },
    buttons: a!buttonLayout(
      primaryButtons: {
        a!buttonWidget(
          label: "Submit Request",
          submit: true,
          style: "SOLID",
          size: "STANDARD",
          loadingIndicator: true,
          saveInto: {
            a!save(local!submitted, true)
            /* Add process start logic here, e.g.: */
            /* a!startProcess(
                 processModel: cons!PM_REQUEST_INTAKE,
                 processParameters: {
                   firstName: local!firstName,
                   lastName: local!lastName,
                   email: local!email,
                   department: local!department,
                   requestType: local!requestType,
                   priority: local!priority,
                   requestTitle: local!requestTitle,
                   description: local!description,
                   targetDate: local!targetDate,
                   attachments: local!attachments
                 },
                 onSuccess: {
                   /* Add success handling logic here */
                 },
                 onError: {
                   a!save(local!errorMessage, "Failed to submit request. Please try again.")
                 }
               ) */
          }
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
)
