# PACE Lab Repository

This repository provides a central place for maintaining PACE Lab materials, the lab handbook, and the public website.

The repository currently uses the following structure:

```text
thePACElab/
├── handbook/           # Lab handbook and onboarding materials
│   └── onboarding/     # New-member onboarding guide
└── website/            # PACE Lab public website project
```

## Lab Handbook

- [New-Member Onboarding Guide](handbook/onboarding/README.md)

The handbook begins with essential information. Additional guidance on data and code management, fieldwork, lab meetings and communication, commonly used templates, and other topics can be added as needed.

## Public Website

The website content, styles, and build scripts are maintained in [`website/`](website/). The website can be maintained and published independently; see the [Website Maintenance Guide](website/README.md) for details.

Internal lab materials are not automatically published on the PACE Lab website. Only content in the `website/` project is included in the website build and deployment process.

> This repository is public. Do not commit passwords, unpublished data, private contact details, or other sensitive information to the handbook or other repository materials.
