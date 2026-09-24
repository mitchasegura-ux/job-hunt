# /job-init - Set up a job search workspace

Invoke the `job-hunting` skill and follow its **Initialize a workspace** section.

`$ARGUMENTS` may be a target directory. Default is the current working
directory.

**Check what already exists first.** If the user has resumes, letters, or a
tracker in a different layout, write the config to point at those files rather
than moving anything. Reorganizing someone's existing work is not an upgrade.

Create the folder shape, initialize the tracker with
`tracker.py init <name>.xlsx`, and write `jobsearch.config.yml` with their
paths, pay floor, schedule constraints, target locations, and search tracks.

Ask for the constraints rather than guessing. Pay floor and schedule are hard
filters used on every future search, and wrong values quietly waste effort for
weeks.

Finish by pointing them at `/job-profile`.
