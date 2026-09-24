# /job-init - Set up a job search workspace

Invoke the `job-hunting` skill and follow its **Initialize a workspace** section.

`$ARGUMENTS` may be a target directory. Default is the current working
directory.

**Check what already exists first.** If the user has resumes, letters, or a
tracker in a different layout, write the config to point at those files rather
than moving anything. Reorganizing someone's existing work is not an upgrade.

Create the folder shape, initialize the tracker with
`tracker.py init <name>.xlsx`, and write `jobsearch.config.yml` with their
paths, pay floor, schedule constraints, target locations, search tracks, and
document formatting.

**Formatting.** Ask which font they want on resumes and letters, and whether
they want the default sizes and margins (resume 10pt / 0.5in, letter 11pt /
0.9in). If their current resume uses a font, suggest matching it. Verify the
font works with `printf x | pandoc -o /tmp/fonttest.pdf --pdf-engine=xelatex -V mainfont="<font>"` before writing it to
`formatting.font`; an uninstalled font makes every PDF render fail. If it is
missing, offer an installed alternative or leave `font` empty for the LaTeX
default.

Ask for the constraints rather than guessing. Pay floor and schedule are hard
filters used on every future search, and wrong values quietly waste effort for
weeks.

Finish by pointing them at `/job-profile`.
