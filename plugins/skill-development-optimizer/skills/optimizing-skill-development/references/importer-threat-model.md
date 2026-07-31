# Importer Threat Model

Apply this profile only when a skill contains external acquisition or cache
code. Do not add importer checks to a skill that only contains instructions,
local deterministic tools, or static references. When the profile applies,
exercise request policy and managed filesystem behavior with deterministic
tests before any live network milestone.

## Required threats

- Minimum request interval survives retries, redirects, and failures.
- Retry-After may lengthen but never shorten the minimum.
- Redirects remain on the exact allowed HTTPS origin and path family.
- Cache paths reject traversal, symlinks, hardlinks, FIFOs, devices, and directories.
- Root/ancestor replacement cannot redirect managed I/O.
- Reads, logs, temporary files, and replacements are anchored to a retained directory boundary.
- Interrupted writes preserve the last valid manifest/page pair.
- Closed handles fail closed; unsupported platform operations produce deterministic errors.
- Live network checks are explicit milestones, not routine edit checks.

## Network boundary

Enforce pacing across every outbound attempt, including the attempt after a
failure or redirect. Measure from a monotonic clock and centralize the gate so a
retry path cannot bypass it. Honor `Retry-After` only when it increases the
delay required by the configured minimum.

Validate every initial and redirected URL before sending the next request.
Require HTTPS, an exact allowed origin, and the declared path family. Reject
scheme changes, user information, lookalike hosts, alternate ports, encoded
path escapes, and redirects outside the family. Bound redirect and retry
counts.

## Filesystem boundary

Treat cache contents and path components as hostile. Retain a descriptor or
equivalent capability for the trusted cache boundary, then resolve managed
reads, logs, staging files, and replacements relative to it. Revalidate types
and identities at use time; a prior path check is not protection against a
concurrent ancestor swap.

Reject traversal and every link or nonregular object, including hardlinked
regular files when exclusive ownership is required. Create temporary files
inside the retained boundary with exclusive semantics. Flush file data and
directory metadata in the correct order, and publish a manifest/page pair only
after both staged values are durable. On interruption, readers must observe the
previous valid pair or the new valid pair, never a mixture.

Keep ownership markers for cleanup targets. Remove only objects whose location,
type, and marker prove they belong to the importer. Preserve unowned
lookalikes. If descriptor-relative or identity-preserving operations are not
supported on the platform, stop with a stable, documented error rather than
falling back to unsafe path-based I/O. Treat reuse of a closed handle as an
error.

## Evidence and milestones

Cover pacing, redirect validation, cache attacks, concurrent replacement,
interrupted publication, cleanup ownership, closed handles, and unsupported
operations with deterministic tests. Use fake clocks, scripted transports,
temporary directories, and injected failures. Record which threats each test
covers.

Request approval before the explicit live check. Keep it small, paced, and
restricted to the configured origin. Record the milestone and outcome, but do
not make routine validation depend on network availability.
