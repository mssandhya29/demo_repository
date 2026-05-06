import json
import zipfile
import uuid

def create_appian_package(interface_name: str, sail_code: str, output_path: str = None):
    if output_path is None:
        output_path = f"{interface_name}.zip"

    object_uuid = str(uuid.uuid4())

    # _manifest.json — matches Appian export schema
    manifest = {
        "appianPackageExportFormatVersion": "1",
        "objects": [
            {
                "type": "Interface",
                "name": interface_name,
                "uuid": object_uuid
            }
        ]
    }

    # interface/<Name>.json — Appian interface object schema
    interface_obj = {
        "entity": {
            "id": object_uuid,
            "name": interface_name,
            "type": "Interface",
            "uuid": object_uuid
        },
        "contents": {
            "sailCode": sail_code
        }
    }

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("_manifest.json", json.dumps(manifest, indent=2))
        zf.writestr(
            f"interface/{interface_name}.json",
            json.dumps(interface_obj, indent=2)
        )

    print(f"Package created: {output_path}")
    return output_path, object_uuid


SAIL_CODE = r"""a!localVariables(
  local!firstName: null,
  local!lastName: null,
  local!email: null,
  local!phone: null,
  local!department: null,
  local!requestType: null,
  local!priority: null,
  local!requestTitle: null,
  local!requestDescription: null,
  local!targetDate: null,
  local!attachments: {},
  local!submitted: false,
  local!showConfirmation: false,
  local!showCancelDialog: false,
  if(
    local!showConfirmation,
    /* ── Confirmation screen ── */
    a!formLayout(
      titleBar: a!headerTemplateSimple(title: "Request Submitted"),
      contents: {
        a!columnsLayout(
          columns: {
            a!columnLayout(
              width: "AUTO",
              showWhen: a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"})
            ),
            a!columnLayout(
              width: if(a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"}), "WIDE_PLUS", "AUTO"),
              contents: {
                a!cardLayout(
                  contents: {
                    a!richTextDisplayField(
                      labelPosition: "COLLAPSED",
                      value: {
                        a!richTextItem(
                          text: "Your intake request has been submitted successfully.",
                          size: "MEDIUM",
                          color: "POSITIVE"
                        )
                      }
                    ),
                    a!richTextDisplayField(
                      labelPosition: "COLLAPSED",
                      value: {
                        a!richTextItem(text: "Submitted by: ", style: "STRONG"),
                        a!richTextItem(
                          text: a!defaultValue(local!firstName, "") & " " & a!defaultValue(local!lastName, "")
                        )
                      }
                    ),
                    a!richTextDisplayField(
                      labelPosition: "COLLAPSED",
                      value: {
                        a!richTextItem(text: "Request: ", style: "STRONG"),
                        a!richTextItem(text: a!defaultValue(local!requestTitle, ""))
                      }
                    ),
                    a!richTextDisplayField(
                      labelPosition: "COLLAPSED",
                      value: {
                        a!richTextItem(text: "Priority: ", style: "STRONG"),
                        a!richTextItem(text: a!defaultValue(local!priority, ""))
                      }
                    ),
                    a!richTextDisplayField(
                      labelPosition: "COLLAPSED",
                      value: {
                        a!richTextItem(text: "Target Date: ", style: "STRONG"),
                        a!richTextItem(
                          text: if(
                            a!isNullOrEmpty(local!targetDate),
                            "Not specified",
                            text(local!targetDate, "dd MMM yyyy")
                          )
                        )
                      }
                    )
                  },
                  style: "STANDARD",
                  padding: "STANDARD",
                  showBorder: true,
                  shape: "SEMI_ROUNDED"
                )
              }
            ),
            a!columnLayout(
              width: "AUTO",
              showWhen: a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"})
            )
          }
        )
      },
      buttons: a!buttonLayout(
        primaryButtons: {
          a!buttonWidget(
            label: "Submit Another Request",
            style: "SOLID",
            value: false,
            saveInto: {
              a!save(local!showConfirmation, false),
              a!save(local!firstName, null),
              a!save(local!lastName, null),
              a!save(local!email, null),
              a!save(local!phone, null),
              a!save(local!department, null),
              a!save(local!requestType, null),
              a!save(local!priority, null),
              a!save(local!requestTitle, null),
              a!save(local!requestDescription, null),
              a!save(local!targetDate, null),
              a!save(local!attachments, {}),
              a!save(local!submitted, false)
            }
          )
        }
      )
    ),
    /* ── Main intake form ── */
    a!formLayout(
      titleBar: a!headerTemplateSimple(title: "Intake Request Form"),
      contents: {
        a!columnsLayout(
          columns: {
            a!columnLayout(
              width: "AUTO",
              showWhen: a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"})
            ),
            a!columnLayout(
              width: if(a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"}), "WIDE_PLUS", "AUTO"),
              contents: {
                /* ── Section 1: Requester Information ── */
                a!sectionLayout(
                  label: "Requester Information",
                  labelHeadingTag: "H2",
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
                        "Engineering",
                        "Marketing",
                        "Sales",
                        "HR",
                        "Finance",
                        "Operations",
                        "Other"
                      },
                      choiceValues: {
                        "engineering",
                        "marketing",
                        "sales",
                        "hr",
                        "finance",
                        "operations",
                        "other"
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
                    )
                  },
                  isCollapsible: false,
                  marginBelow: "STANDARD"
                ),
                /* ── Section 2: Request Details ── */
                a!sectionLayout(
                  label: "Request Details",
                  labelHeadingTag: "H2",
                  contents: {
                    a!columnsLayout(
                      columns: {
                        a!columnLayout(
                          contents: {
                            a!dropdownField(
                              label: "Request Type",
                              labelPosition: "ABOVE",
                              choiceLabels: {
                                "New Feature",
                                "Bug Fix",
                                "Access Request",
                                "Data Request",
                                "Process Change",
                                "Infrastructure",
                                "Other"
                              },
                              choiceValues: {
                                "new_feature",
                                "bug_fix",
                                "access_request",
                                "data_request",
                                "process_change",
                                "infrastructure",
                                "other"
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
                  },
                  isCollapsible: false,
                  marginBelow: "STANDARD"
                ),
                /* ── Section 3: Attachments ── */
                a!sectionLayout(
                  label: "Attachments",
                  labelHeadingTag: "H2",
                  contents: {
                    a!fileUploadField(
                      label: "Supporting Documents",
                      labelPosition: "ABOVE",
                      instructions: "Attach any relevant documents, screenshots, or specifications",
                      target: a!documentsFolder(
                        /* Replace with your documents folder constant */
                        cons!INTAKE_DOCUMENTS_FOLDER
                      ),
                      saveInto: local!attachments,
                      buttonStyle: "SECONDARY",
                      validations: {}
                    )
                  },
                  isCollapsible: true,
                  marginBelow: "STANDARD"
                ),
                /* ── Section 4: Priority Guidance ── */
                a!sectionLayout(
                  label: "Priority Guidance",
                  labelHeadingTag: "H2",
                  contents: {
                    a!cardGroupLayout(
                      labelPosition: "COLLAPSED",
                      cards: {
                        a!cardLayout(
                          contents: {
                            a!richTextDisplayField(
                              labelPosition: "COLLAPSED",
                              value: {
                                a!richTextItem(text: "Low", style: "STRONG"),
                                a!richTextItem(
                                  text: char(10) & "Nice-to-have improvements with no time constraint."
                                )
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
                                a!richTextItem(text: "Medium", style: "STRONG"),
                                a!richTextItem(
                                  text: char(10) & "Important but not time-critical. Standard queue."
                                )
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
                                a!richTextItem(text: "High", style: "STRONG", color: "ACCENT"),
                                a!richTextItem(
                                  text: char(10) & "Significant business impact. Needs prompt attention."
                                )
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
                                a!richTextItem(text: "Critical", style: "STRONG", color: "NEGATIVE"),
                                a!richTextItem(
                                  text: char(10) & "System down or major business blocker. Immediate escalation."
                                )
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
                    )
                  },
                  isCollapsible: true,
                  marginBelow: "STANDARD"
                )
              }
            ),
            a!columnLayout(
              width: "AUTO",
              showWhen: a!isPageWidth({"DESKTOP", "DESKTOP_WIDE"})
            )
          }
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
)"""

output_zip, pkg_uuid = create_appian_package(
    interface_name="IntakeRequestForm",
    sail_code=SAIL_CODE,
    output_path="/home/user/demo_repository/IntakeRequestForm.zip"
)

# Also write raw SAIL as plain text fallback
with open("/home/user/demo_repository/IntakeRequestForm.sail", "w") as f:
    f.write(SAIL_CODE)

print(f"UUID used: {pkg_uuid}")
print("Plain SAIL file written: IntakeRequestForm.sail")
