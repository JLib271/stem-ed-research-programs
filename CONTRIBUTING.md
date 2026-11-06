# Contributing

Thank you for helping prospective students find graduate programs in STEM+ education research.

## What belongs here

Graduate programs where students can do **discipline-based education research (DBER)**:
research on teaching and learning in a STEM discipline, usually supervised by faculty in a
science, engineering, or mathematics department, college, or institute. Programs in schools of
education qualify when a named faculty member supervises DBER students in a specific discipline.

Include programs and research groups whether or not they are taking students right now.
Remove a program only when it no longer exists, not when it stops admitting students.

List one program per institution and discipline. If one department offers DBER in two
disciplines, list both in the same file's `disciplines`.

## Add or update a program

You can do this in any of three ways:

1. **Email** the maintainer (see the README) with the five fields below.
2. **Issue form:** [Add a program](../../issues/new?template=add_program.yml) or
   [Update a program](../../issues/new?template=update_program.yml). A maintainer turns it into a file.
3. **Pull request:** add or edit a file in `programs/` (copy an existing one), then run the checks below.

### The fields

```yaml
id: example-university-chemistry     # same as the file name: institution, then discipline
institution:
  name: Example University
  country: United States
  # ror: https://ror.org/0xxxxxxxx   # optional ROR identifier
home_department: Department of Chemistry   # add partner units after "with"
degree_types: [MS, PhD]                    # BS, MA, MS, MEd, MAT, EdD, PhD, Certificate
disciplines: [chemistry]                   # ids from schema/disciplines.json
dber_faculty:
  - name: Firstname Lastname
url: https://example.edu/chem-ed           # optional: program, group, or department page
source: https://example.edu/chem-ed        # where this came from, or "Submitted by <name>, <role>"
last_verified: 2026-11-06                  # when someone last confirmed it
# needs_check: [home_department]           # fields still to confirm with the program
```

### Faculty listings

List faculty only when they agree to be listed, or when the program publicly lists them as
supervising education research students. Do not add email addresses or other contact details.
Anyone can ask to be removed or corrected.

### Checks

```bash
pip install -r requirements.txt
python scripts/build.py          # validates every file and regenerates the README table
python scripts/build.py --check  # what CI runs
```

Commit the regenerated `README.md` with your change.

## Keeping the list current

* Each entry's `last_verified` date shows how fresh it is. When you confirm an entry, update the date.
* A scheduled workflow checks every link once a month and lists broken ones in its run summary.
* Entries that cannot be confirmed for two years may be marked `needs_check` or removed.

## Publishing the website

The searchable website in `site/` is built and published by `.github/workflows/pages.yml`.
To turn it on: in the repository's **Settings → Pages**, set **Source** to **GitHub Actions**.
The site appears at https://jlib271.github.io/dber-graduate-programs/ after the next push to `main`
(or run the workflow by hand from the Actions tab).
