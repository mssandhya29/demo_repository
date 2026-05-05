a!localVariables(
  /* ── Requester fields ── */
  local!firstName: null,
  local!lastName: null,
  local!email: null,
  local!phone: null,
  local!department: null,

  /* ── Request fields ── */
  local!requestType: null,
  local!priority: null,
  local!requestTitle: null,
  local!requestDescription: null,
  local!targetDate: null,
  local!quantity: 0,
  local!attachments: {},

  /* ── UI state ── */
  local!submitted: false,
  local!showConfirmation: false,
  local!showCancelDialog: false,

  /* ── Sample display data ── */
  local!recentRequests: {
    a!map(id: "REQ-2024-001", title: "Portal Redesign",   status: "In Progress", priority: "High",     submittedDate: today() - 10),
    a!map(id: "REQ-2024-002", title: "Access Request",    status: "Complete",    priority: "Low",      submittedDate: today() - 25),
    a!map(id: "REQ-2024-003", title: "Data Migration",    status: "Pending",     priority: "Critical", submittedDate: today() - 3),
    a!map(id: "REQ-2024-004", title: "Report Automation", status: "In Progress", priority: "Medium",   submittedDate: today() - 7)
  },

  local!monthlyCounts: {42, 58, 37, 61, 55, 48},

  /* ══════════════════════════════════════════
     TOP-LEVEL: a!headerContentLayout
     ══════════════════════════════════════════ */
  a!headerContentLayout(
    header: {
      a!cardLayout(
        contents: {
          a!sideBySideLayout(
            items: {
              a!sideBySideItem(
                width: "MINIMIZE",
                item: a!imageField(
                  labelPosition: "COLLAPSED",
                  images: a!userImage(user: loggedInUser()),
                  size: "SMALL"
                )
              ),
              a!sideBySideItem(
                item: a!richTextDisplayField(
                  labelPosition: "COLLAPSED",
                  value: {
                    a!richTextItem(
                      text: "Intake Request Portal",
                      size: "LARGE",
                      style: "STRONG"
                    ),
                    a!richTextItem(
                      text: char(10) & "Submit and track your business requests",
                      size: "SMALL",
                      color: "SECONDARY"
                    )
                  }
                )
              )
            },
            alignVertical: "MIDDLE",
            stackWhen: {"PHONE"}
          )
        },
        style: "ACCENT",
        padding: "STANDARD"
      )
    },
    contents: {
      a!columnsLayout(
        columns: {
          /* Left margin hidden on mobile */
          a!columnLayout(
            width: "AUTO",
            showWhen: a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"})
          ),

          /* ── Main content ── */
          a!columnLayout(
            width: if(a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"}), "WIDE_PLUS", "AUTO"),
            contents: {

              /* ── Milestone tracker ── */
              a!milestoneField(
                labelPosition: "COLLAPSED",
                steps: {
                  "Submit Request",
                  "Review",
                  "Approval",
                  "In Progress",
                  "Complete"
                },
                active: 1
              ),

              /* ── KPI cards ── */
              a!cardGroupLayout(
                labelPosition: "COLLAPSED",
                cards: {
                  a!cardLayout(
                    contents: {
                      a!richTextDisplayField(
                        labelPosition: "COLLAPSED",
                        value: {
                          a!richTextItem(text: "Open Requests", style: "STRONG", size: "SMALL"),
                          a!richTextItem(text: char(10) & "12", size: "LARGE", style: "STRONG", color: "ACCENT")
                        }
                      )
                    },
                    style: "STANDARD",
                    padding: "STANDARD",
                    showBorder: true,
                    shape: "SEMI_ROUNDED"
                  ),
                  a!cardLayout(
                    contents: {
                      a!richTextDisplayField(
                        labelPosition: "COLLAPSED",
                        value: {
                          a!richTextItem(text: "In Progress", style: "STRONG", size: "SMALL"),
                          a!richTextItem(text: char(10) & "5", size: "LARGE", style: "STRONG", color: "STANDARD")
                        }
                      )
                    },
                    style: "STANDARD",
                    padding: "STANDARD",
                    showBorder: true,
                    shape: "SEMI_ROUNDED"
                  ),
                  a!cardLayout(
                    contents: {
                      a!richTextDisplayField(
                        labelPosition: "COLLAPSED",
                        value: {
                          a!richTextItem(text: "Completed This Month", style: "STRONG", size: "SMALL"),
                          a!richTextItem(text: char(10) & "28", size: "LARGE", style: "STRONG", color: "POSITIVE")
                        }
                      )
                    },
                    style: "STANDARD",
                    padding: "STANDARD",
                    showBorder: true,
                    shape: "SEMI_ROUNDED"
                  ),
                  a!cardLayout(
                    contents: {
                      a!richTextDisplayField(
                        labelPosition: "COLLAPSED",
                        value: {
                          a!richTextItem(text: "Critical / Overdue", style: "STRONG", size: "SMALL"),
                          a!richTextItem(text: char(10) & "2", size: "LARGE", style: "STRONG", color: "NEGATIVE")
                        }
                      )
                    },
                    style: "STANDARD",
                    padding: "STANDARD",
                    showBorder: true,
                    shape: "SEMI_ROUNDED"
                  )
                },
                spacing: "STANDARD",
                cardWidth: "MEDIUM",
                cardHeight: "AUTO"
              ),

              /* ── Two-column layout: chart + grid ── */
              a!columnsLayout(
                columns: {
                  a!columnLayout(
                    width: "MEDIUM",
                    contents: {
                      a!sectionLayout(
                        label: "Requests by Month",
                        labelHeadingTag: "H2",
                        contents: {
                          a!columnChartField(
                            label: "Requests by Month",
                            labelPosition: "COLLAPSED",
                            categories: {"Jan", "Feb", "Mar", "Apr", "May", "Jun"},
                            series: {
                              a!chartSeries(
                                label: "2024",
                                data: local!monthlyCounts
                              )
                            },
                            colorScheme: "RAINFOREST",
                            showLegend: true,
                            height: "MEDIUM"
                          )
                        },
                        marginBelow: "STANDARD"
                      )
                    }
                  ),
                  a!columnLayout(
                    contents: {
                      a!sectionLayout(
                        label: "Recent Requests",
                        labelHeadingTag: "H2",
                        contents: {
                          a!gridField(
                            labelPosition: "COLLAPSED",
                            data: local!recentRequests,
                            columns: {
                              a!gridColumn(
                                label: "ID",
                                value: a!richTextDisplayField(
                                  labelPosition: "COLLAPSED",
                                  value: {
                                    a!richTextItem(text: fv!row.id, style: "STRONG")
                                  }
                                )
                              ),
                              a!gridColumn(
                                label: "Title",
                                value: fv!row.title
                              ),
                              a!gridColumn(
                                label: "Priority",
                                value: a!tagField(
                                  labelPosition: "COLLAPSED",
                                  tags: {
                                    a!tagItem(
                                      text: fv!row.priority,
                                      backgroundColor: if(
                                        fv!row.priority = "Critical", "NEGATIVE",
                                        if(
                                          fv!row.priority = "High", "ACCENT",
                                          if(
                                            fv!row.priority = "Medium", "WARN",
                                            "SECONDARY"
                                          )
                                        )
                                      )
                                    )
                                  }
                                )
                              ),
                              a!gridColumn(
                                label: "Status",
                                value: a!richTextDisplayField(
                                  labelPosition: "COLLAPSED",
                                  value: {
                                    a!richTextItem(
                                      text: fv!row.status,
                                      color: if(
                                        fv!row.status = "Complete", "POSITIVE",
                                        if(fv!row.status = "Pending", "SECONDARY", "STANDARD")
                                      )
                                    )
                                  }
                                )
                              )
                            },
                            rowHeader: 1
                          )
                        },
                        marginBelow: "STANDARD"
                      )
                    }
                  )
                },
                stackWhen: {"PHONE", "TABLET_PORTRAIT"}
              ),

              /* ════════════════════════════
                 INTAKE FORM SECTION
                 ════════════════════════════ */
              a!sectionLayout(
                label: "Submit a New Request",
                labelHeadingTag: "H2",
                isCollapsible: true,
                contents: {
                  if(
                    local!showConfirmation,
                    a!messageBanner(
                      icon: "check-circle",
                      primaryText: "Request submitted successfully!"
                    ),
                    a!formLayout(
                      contents: {

                        a!headingField(
                          text: "Requester Information",
                          size: "MEDIUM",
                          headingTag: "H3"
                        ),

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
                                  validations: if(
                                    and(local!submitted, a!isNullOrEmpty(local!firstName)),
                                    "First name is required",
                                    null
                                  )
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
                                  validations: if(
                                    and(local!submitted, a!isNullOrEmpty(local!lastName)),
                                    "Last name is required",
                                    null
                                  )
                                )
                              }
                            )
                          },
                          stackWhen: {"PHONE"}
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
                                  placeholder: "name@company.com",
                                  validations: {
                                    if(
                                      and(local!submitted, a!isNullOrEmpty(local!email)),
                                      "Email address is required",
                                      null
                                    ),
                                    if(
                                      and(
                                        a!isNotNullOrEmpty(local!email),
                                        not(contains(local!email, "@"))
                                      ),
                                      "Please enter a valid email address",
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
                                  instructions: "Optional — include country code for international numbers"
                                )
                              }
                            )
                          },
                          stackWhen: {"PHONE"}
                        ),

                        a!dropdownField(
                          label: "Department",
                          labelPosition: "ABOVE",
                          choiceLabels: {
                            "Engineering", "Marketing", "Sales",
                            "HR", "Finance", "Operations", "Other"
                          },
                          choiceValues: {
                            "engineering", "marketing", "sales",
                            "hr", "finance", "operations", "other"
                          },
                          value: local!department,
                          saveInto: local!department,
                          placeholder: "Select your department",
                          required: true,
                          validations: if(
                            and(local!submitted, a!isNullOrEmpty(local!department)),
                            "Department is required",
                            null
                          )
                        ),

                        a!headingField(
                          text: "Request Details",
                          size: "MEDIUM",
                          headingTag: "H3"
                        ),

                        a!columnsLayout(
                          columns: {
                            a!columnLayout(
                              contents: {
                                a!dropdownField(
                                  label: "Request Type",
                                  labelPosition: "ABOVE",
                                  choiceLabels: {
                                    "New Feature", "Bug Fix", "Access Request",
                                    "Data Request", "Process Change",
                                    "Infrastructure", "Other"
                                  },
                                  choiceValues: {
                                    "new_feature", "bug_fix", "access_request",
                                    "data_request", "process_change",
                                    "infrastructure", "other"
                                  },
                                  value: local!requestType,
                                  saveInto: local!requestType,
                                  placeholder: "Select request type",
                                  required: true,
                                  validations: if(
                                    and(local!submitted, a!isNullOrEmpty(local!requestType)),
                                    "Request type is required",
                                    null
                                  )
                                )
                              }
                            ),
                            a!columnLayout(
                              contents: {
                                a!radioButtonField(
                                  label: "Priority",
                                  labelPosition: "ABOVE",
                                  choiceLabels: {"Low", "Medium", "High", "Critical"},
                                  choiceValues: {"Low", "Medium", "High", "Critical"},
                                  value: local!priority,
                                  saveInto: local!priority,
                                  choiceLayout: "STACKED",
                                  required: true,
                                  validations: if(
                                    and(local!submitted, a!isNullOrEmpty(local!priority)),
                                    "Priority is required",
                                    null
                                  )
                                )
                              }
                            )
                          },
                          stackWhen: {"PHONE", "TABLET_PORTRAIT"}
                        ),

                        a!textField(
                          label: "Request Title",
                          labelPosition: "ABOVE",
                          value: local!requestTitle,
                          saveInto: local!requestTitle,
                          required: true,
                          placeholder: "Brief title summarising your request",
                          instructions: "Keep it concise — 10 words or fewer",
                          validations: {
                            if(
                              and(local!submitted, a!isNullOrEmpty(local!requestTitle)),
                              "Request title is required",
                              null
                            ),
                            if(
                              and(
                                a!isNotNullOrEmpty(local!requestTitle),
                                len(local!requestTitle) < 5
                              ),
                              "Title must be at least 5 characters",
                              null
                            )
                          }
                        ),

                        a!paragraphField(
                          label: "Description",
                          labelPosition: "ABOVE",
                          value: local!requestDescription,
                          saveInto: local!requestDescription,
                          required: true,
                          placeholder: "Describe your request in detail — include business justification, expected outcome, and any dependencies",
                          height: "MEDIUM",
                          validations: {
                            if(
                              and(local!submitted, a!isNullOrEmpty(local!requestDescription)),
                              "Description is required",
                              null
                            ),
                            if(
                              and(
                                a!isNotNullOrEmpty(local!requestDescription),
                                len(local!requestDescription) < 20
                              ),
                              "Please provide a more detailed description (at least 20 characters)",
                              null
                            )
                          }
                        ),

                        a!columnsLayout(
                          columns: {
                            a!columnLayout(
                              contents: {
                                a!integerField(
                                  label: "Estimated Effort (days)",
                                  labelPosition: "ABOVE",
                                  value: local!quantity,
                                  saveInto: local!quantity,
                                  placeholder: "0",
                                  validations: if(
                                    and(
                                      a!isNotNullOrEmpty(local!quantity),
                                      tointeger(local!quantity) < 0
                                    ),
                                    "Effort must be 0 or greater",
                                    null
                                  )
                                )
                              }
                            ),
                            a!columnLayout(
                              contents: {
                                a!dateField(
                                  label: "Target Completion Date",
                                  labelPosition: "ABOVE",
                                  value: local!targetDate,
                                  saveInto: local!targetDate,
                                  instructions: "Preferred date — subject to team capacity",
                                  validations: if(
                                    and(
                                      a!isNotNullOrEmpty(local!targetDate),
                                      local!targetDate < today()
                                    ),
                                    "Target date cannot be in the past",
                                    null
                                  )
                                )
                              }
                            )
                          },
                          stackWhen: {"PHONE"}
                        ),

                        a!fileUploadField(
                          label: "Supporting Documents",
                          labelPosition: "ABOVE",
                          instructions: "Attach any relevant documents, screenshots, or specifications",
                          target: a!documentsFolder(null),
                          saveInto: local!attachments,
                          buttonStyle: "SECONDARY",
                          validations: {}
                        ),

                        a!checkboxField(
                          label: "Acknowledgement",
                          labelPosition: "ABOVE",
                          choiceLabels: {
                            "I confirm the information provided is accurate and complete"
                          },
                          choiceValues: {true},
                          value: local!submitted,
                          saveInto: local!submitted
                        ),

                        a!progressBarField(
                          label: "Form Completion",
                          labelPosition: "ABOVE",
                          percentage: if(
                            and(
                              a!isNotNullOrEmpty(local!firstName),
                              a!isNotNullOrEmpty(local!lastName),
                              a!isNotNullOrEmpty(local!email),
                              a!isNotNullOrEmpty(local!department),
                              a!isNotNullOrEmpty(local!requestType),
                              a!isNotNullOrEmpty(local!priority),
                              a!isNotNullOrEmpty(local!requestTitle),
                              a!isNotNullOrEmpty(local!requestDescription)
                            ),
                            100,
                            tointeger(
                              if(a!isNotNullOrEmpty(local!firstName), 12, 0) +
                              if(a!isNotNullOrEmpty(local!lastName), 12, 0) +
                              if(a!isNotNullOrEmpty(local!email), 13, 0) +
                              if(a!isNotNullOrEmpty(local!department), 13, 0) +
                              if(a!isNotNullOrEmpty(local!requestType), 12, 0) +
                              if(a!isNotNullOrEmpty(local!priority), 12, 0) +
                              if(a!isNotNullOrEmpty(local!requestTitle), 13, 0) +
                              if(a!isNotNullOrEmpty(local!requestDescription), 13, 0)
                            )
                          ),
                          color: if(
                            and(
                              a!isNotNullOrEmpty(local!firstName),
                              a!isNotNullOrEmpty(local!lastName),
                              a!isNotNullOrEmpty(local!email),
                              a!isNotNullOrEmpty(local!department),
                              a!isNotNullOrEmpty(local!requestType),
                              a!isNotNullOrEmpty(local!priority),
                              a!isNotNullOrEmpty(local!requestTitle),
                              a!isNotNullOrEmpty(local!requestDescription)
                            ),
                            "POSITIVE",
                            "ACCENT"
                          )
                        )

                      },
                      buttons: a!buttonLayout(
                        primaryButtons: {
                          a!buttonWidget(
                            label: "Submit Request",
                            style: "SOLID",
                            submit: true,
                            value: true,
                            saveInto: {
                              a!save(local!submitted, true),
                              if(
                                and(
                                  a!isNotNullOrEmpty(local!firstName),
                                  a!isNotNullOrEmpty(local!lastName),
                                  a!isNotNullOrEmpty(local!email),
                                  a!isNotNullOrEmpty(local!department),
                                  a!isNotNullOrEmpty(local!requestType),
                                  a!isNotNullOrEmpty(local!priority),
                                  a!isNotNullOrEmpty(local!requestTitle),
                                  a!isNotNullOrEmpty(local!requestDescription)
                                ),
                                a!save(local!showConfirmation, true),
                                a!save(local!showConfirmation, false)
                              )
                            }
                          )
                        },
                        secondaryButtons: {
                          a!buttonWidget(
                            label: "Cancel",
                            style: "OUTLINE",
                            value: true,
                            saveInto: local!showCancelDialog
                          )
                        }
                      )
                    )
                  )
                },
                marginBelow: "STANDARD"
              )

            }
          ),

          /* Right margin hidden on mobile */
          a!columnLayout(
            width: "AUTO",
            showWhen: a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"})
          )
        }
      )
    }
  )
)
