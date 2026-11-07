# COGS Community Framework

### Circle of Good Samaritans / Community Organizing & Growth System

### 🔗 Website: **https://ai-prince-1.github.io/cogs-community-framework-/**
The whole framework as an easy-to-read site: manifesto, handbook, playbooks, meeting templates and roles.


What if humanity's next great innovation is not a new technology, but a better way to organize ourselves?

Modern society has unprecedented access to information, yet rising loneliness, declining trust, social fragmentation, and growing polarization.

COGS is an open-source community framework designed to help small groups of people support one another, learn together, build resilience, and improve their communities.

Inspired by Agile, open-source software, systems thinking, and centuries of lessons from both successful and failed institutions, COGS provides a lightweight protocol for human flourishing.

COGS is not a religion.

It is not a political movement.

It is not a self-help brand.

It is a practical framework for people who want stronger communities and better lives.

## Start Here

### Core Documents

- [Manifesto](docs/manifesto.md)
- [Constitution](docs/constitution.md)
- [Handbook](docs/handbook.md)

### Circle Roles

- [Facilitator](roles/facilitator.md)
- [Steward](roles/steward.md)
- [Scribe](roles/scribe.md)
- [Bridge](roles/bridge.md)

### Playbooks

- [Launch a Circle](playbooks/circle-launch.md)
- [Conflict Resolution](playbooks/conflict-resolution.md)
- [Seeding Ceremony](playbooks/seeding-ceremony.md): when a Circle grows past its size limit and splits

### Meeting Templates

- [Weekly Gathering](meetings/weekly-gathering.md): the 70-minute heartbeat
- [Season Opening](meetings/season-opening.md): Week 1
- [Mid-Season Check-In](meetings/mid-season-checkin.md): Week 6
- [Season Retrospective](meetings/retrospective.md): Week 12
- [Season Review](meetings/season-review.md): the one-page Season Summary

### Reference

- [Anti-Cult Safeguards](docs/anti-cult-safeguards.md)
- [Glossary](docs/glossary.md)
- [Brand Assets](branding/assets.md)

## Quick Start

1. **Find 3–7 people** (4–6 is ideal) you'd show up for every week.
2. **Read the [Manifesto](docs/manifesto.md) together** and decide whether it fits.
3. **Hold a [Season Opening](meetings/season-opening.md)**: choose 2–3 life domains and set personal intentions.
4. **Meet weekly for 12 weeks** using the [Weekly Gathering](meetings/weekly-gathering.md) format. Rotate the Facilitator.
5. **Close the Season with a [Retrospective](meetings/retrospective.md)**, then decide what to change.

The [Launch a Circle](playbooks/circle-launch.md) playbook walks through each step.

## Improving the Framework

COGS changes through public proposals, like open-source software:

- Small fixes: open a pull request (see [CONTRIBUTING](CONTRIBUTING.md)).
- Changes to how Circles work: write an [RFC](rfc/README.md) using the [template](rfc/template.md).
- Version history: [CHANGELOG](CHANGELOG.md).

## How the website works

| Layer | What it is |
|---|---|
| **Content** | The Markdown files in this repo (`docs/`, `playbooks/`, `meetings/`, `roles/` …). They are the single source of truth. |
| **Build** | `site/build.py` turns them into web pages with a shared design (`site/template.html`, `site/home.html`, `site/style.css`). |
| **Hosting** | GitHub Actions rebuilds the site on every change to `main` and pushes it to the `gh-pages` branch, which GitHub Pages serves. Free, no server. |

To preview locally: `pip install markdown && python site/build.py && python -m http.server -d _site`.

## License

[Creative Commons Attribution-ShareAlike 4.0](LICENSE). Use it, adapt it and fork it; credit the source and share your changes under the same license.
