#!/usr/bin/env bash
# Copyright 2026 Knoban LLC
# SPDX-License-Identifier: MIT
# (https://github.com/KnobanLabs/sdlc)

# The triage check (CONTRIBUTING.md, Triaging Issues): adds the `triage` label
# to every open issue missing a Priority, an Effort or an area label, so it
# comes back to the triage queue.
#
#   scripts/triage-fields.sh [--dry-run]
#
# --dry-run lists the issues it would label and writes nothing. It needs gh
# and jq, and reads the repository from GH_REPO, then GITHUB_REPOSITORY, then
# the clone's. In a workflow gh takes GH_TOKEN; with issues read access alone
# it can read the fields, and labelling needs issues write. It only ever adds
# `triage`: it never sets, changes or clears a field, and never removes a
# label. Pull requests and closed issues are left alone. It exits 1 when it
# couldn't read the issues or label one, after labelling what it could.

set -euo pipefail

# The label that puts an issue back in the triage queue.
TRIAGE=triage
# The organization issue fields every triaged issue has a value for.
FIELDS='["Priority", "Effort"]'
# The area labels, one of which every triaged issue carries. CONTRIBUTING.md
# lists them; a new one goes here, in .github/labels.json and in
# .github/labeler.yaml.
AREA_LABELS='["plugin", "ci", "config", "documentation"]'

dry_run=false
case "${1:-}" in
  --dry-run) dry_run=true ;;
  '') ;;
  *)
    echo "usage: $0 [--dry-run]" >&2
    exit 2
    ;;
esac

repo=${GH_REPO:-${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}}

# The open issues, without pull requests, as one JSON array.
issues=$(gh api --paginate "repos/$repo/issues?state=open&per_page=100" |
  jq -s '[.[][] | select(.pull_request == null)]')

# A listing without issue_field_values means the token can't read the fields,
# and one where no open issue shows a field means the token can't read it or
# it was renamed, rather than that no issue has one: labelling every open issue
# then would bury the triage queue. So a repository whose open issues all lack
# that field fails the run too.
unread=$(jq -r 'map(select(has("issue_field_values") | not)) | first | .number // empty' <<< "$issues")
if [[ -n "$unread" ]]; then
  echo "✗ The listing shows no fields for #$unread: the token can't read issue fields. Nothing was labelled." >&2
  exit 1
fi
unseen=$(jq -r --argjson fields "$FIELDS" '
  if length == 0 then empty else
    ([.[].issue_field_values[].issue_field_name] | unique) as $shown
    | $fields - $shown | join(" or ") | select(. != "")
  end' <<< "$issues")
if [[ -n "$unseen" ]]; then
  echo "✗ None of the open issues shows a $unseen: the token can't read the field, or it was renamed. Nothing was labelled." >&2
  exit 1
fi

# Each open issue missing something: its number, URL, title, what it is
# missing, and whether it already carries the label.
incomplete=$(jq -c --argjson fields "$FIELDS" --argjson areas "$AREA_LABELS" --arg triage "$TRIAGE" '
  .[]
  | ([.issue_field_values[].issue_field_name]) as $set
  | ([.labels[].name]) as $labels
  | {
      number,
      url: .html_url,
      title,
      missing: (($fields - $set) + (if ($areas - ($areas - $labels)) == [] then ["an area label"] else [] end)),
      labelled: ($labels | index($triage) != null)
    }
  | select(.missing != [])' <<< "$issues")

checked=$(jq length <<< "$issues")
count=0
already=0
rows=()
failed=0
while IFS= read -r issue; do
  [[ -z "$issue" ]] && continue
  count=$((count + 1))
  number=$(jq -r .number <<< "$issue")
  # A title is free text: keep it to one line, and from closing the table's
  # cell or making a link, an image or HTML in the summary. The control
  # characters and the bidi overrides go too, which the log viewer would act
  # on. An escaped `[` also keeps the runner from reading `##[` as a command.
  title=$(jq -r '.title
    | gsub("[\\s\u0085]+"; " ") | ltrimstr(" ") | rtrimstr(" ")
    | gsub("[\u0000-\u001f\u007f‪-‮⁦-⁩]"; "")
    | gsub("(?<c>[|\\\\\\[\\]<>])"; "\\\(.c)")' <<< "$issue")
  missing=$(jq -r '.missing | join(", ")' <<< "$issue")
  url=$(jq -r .url <<< "$issue")
  if [[ $(jq -r .labelled <<< "$issue") == true ]]; then
    already=$((already + 1))
    action='already labelled'
  elif $dry_run; then
    action="would label \`$TRIAGE\`"
  elif gh api --silent -X POST "repos/$repo/issues/$number/labels" -f "labels[]=$TRIAGE"; then
    action="labelled \`$TRIAGE\`"
  else
    echo "✗ #$number: couldn't add the label." >&2
    action='failed to label'
    failed=1
  fi
  rows+=("| [#$number]($url) $title | $missing | $action |")
done <<< "$incomplete"

{
  echo '## Triage fields'
  echo
  note=''
  $dry_run && note=' A dry run: nothing written.'
  echo "Open issues checked: $checked. Missing a Priority, an Effort or an area label: $count, of which already labelled \`$TRIAGE\`: $already.$note"
  if ((count)); then
    echo
    echo '| Issue | Missing | Action |'
    echo '| --- | --- | --- |'
    printf '%s\n' "${rows[@]}"
  fi
} | tee -a "${GITHUB_STEP_SUMMARY:-/dev/null}"

exit "$failed"
